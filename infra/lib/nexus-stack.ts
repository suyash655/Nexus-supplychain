import * as cdk from 'aws-cdk-lib';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as cloudwatch_actions from 'aws-cdk-lib/aws-cloudwatch-actions';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as acm from 'aws-cdk-lib/aws-certificatemanager';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';

export interface NexusStackProps extends cdk.StackProps {
  /**
   * ARN of the manually validated ACM certificate in the deployment region.
   * Required for HTTPS termination at the ALB.
   */
  certificateArn: string;
}

export class NexusStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props: NexusStackProps) {
    super(scope, id, props);

    // ── Networking (VPC) ──
    const vpc = new ec2.Vpc(this, 'NexusVpc', {
      maxAzs: 2,
      natGateways: 1,
    });

    // ── Storage (S3 & RDS) ──
    const docBucket = new s3.Bucket(this, 'NexusDocumentsBucket', {
      encryption: s3.BucketEncryption.S3_MANAGED,
      versioned: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    const dbSecret = new secretsmanager.Secret(this, 'NexusDbSecret', {
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ username: 'nexus' }),
        generateStringKey: 'password',
        excludePunctuation: true,
      },
    });
    
    const db = new rds.DatabaseInstance(this, 'NexusDb', {
      engine: rds.DatabaseInstanceEngine.postgres({ version: rds.PostgresEngineVersion.VER_16 }),
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
      vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
      credentials: rds.Credentials.fromSecret(dbSecret),
      databaseName: 'nexus',
      deletionProtection: true,
      backupRetention: cdk.Duration.days(7),
    });

    // ── Compute (ECS Cluster) ──
    const cluster = new ecs.Cluster(this, 'NexusCluster', { vpc });
    
    // ── Backend Configuration ──
    const backendRepo = ecr.Repository.fromRepositoryName(this, 'NexusBackendRepo', 'nexus-backend');
    
    const backendTaskDef = new ecs.FargateTaskDefinition(this, 'NexusBackendTask', {
      memoryLimitMiB: 1024,
      cpu: 512,
    });
    
    const backendLogGroup = new logs.LogGroup(this, 'NexusBackendLogs', {
      retention: logs.RetentionDays.ONE_MONTH,
    });
    
    backendTaskDef.addContainer('NexusApi', {
      image: ecs.ContainerImage.fromEcrRepository(backendRepo, 'latest'),
      portMappings: [{ containerPort: 8000 }],
      secrets: {
        DB_PASSWORD: ecs.Secret.fromSecretsManager(dbSecret, 'password'),
      },
      environment: {
        DATABASE_URL: `postgresql+asyncpg://nexus:$(DB_PASSWORD)@${db.instanceEndpoint.hostname}/nexus`,
        ENVIRONMENT: 'production',
      },
      logging: ecs.LogDrivers.awsLogs({ streamPrefix: 'api', logGroup: backendLogGroup }),
      healthCheck: {
        command: ['CMD-SHELL', 'curl -f http://localhost:8000/ || exit 1'],
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
        retries: 3,
      },
    });

    backendTaskDef.taskRole.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess')
    );
    
    backendTaskDef.taskRole.addToPrincipalPolicy(new iam.PolicyStatement({
      actions: ['s3:GetObject', 's3:ListBucket'],
      resources: [docBucket.bucketArn, `${docBucket.bucketArn}/*`],
    }));

    const backendService = new ecs.FargateService(this, 'NexusBackendService', {
      cluster,
      taskDefinition: backendTaskDef,
      desiredCount: 2,
      assignPublicIp: false,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
    });

    // ── Frontend Configuration ──
    const frontendRepo = ecr.Repository.fromRepositoryName(this, 'NexusFrontendRepo', 'nexus-frontend');
    
    const frontendTaskDef = new ecs.FargateTaskDefinition(this, 'NexusFrontendTask', {
      memoryLimitMiB: 512,
      cpu: 256,
    });

    const frontendLogGroup = new logs.LogGroup(this, 'NexusFrontendLogs', {
      retention: logs.RetentionDays.ONE_MONTH,
    });

    frontendTaskDef.addContainer('NexusFrontend', {
      image: ecs.ContainerImage.fromEcrRepository(frontendRepo, 'latest'),
      portMappings: [{ containerPort: 3000 }],
      environment: {
        NODE_ENV: 'production',
      },
      logging: ecs.LogDrivers.awsLogs({ streamPrefix: 'ui', logGroup: frontendLogGroup }),
    });

    const frontendService = new ecs.FargateService(this, 'NexusFrontendService', {
      cluster,
      taskDefinition: frontendTaskDef,
      desiredCount: 2,
      assignPublicIp: false,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
    });

    // ── Application Load Balancer & Routing ──
    const alb = new elbv2.ApplicationLoadBalancer(this, 'NexusAlb', { vpc, internetFacing: true });
    
    // Import manually validated ACM Certificate
    const certificate = acm.Certificate.fromCertificateArn(this, 'NexusCert', props.certificateArn);

    // Create HTTPS Listener
    const httpsListener = alb.addListener('HttpsListener', { 
      port: 443, 
      certificates: [certificate],
      open: true 
    });

    // Default Action: Route to Frontend
    httpsListener.addTargets('FrontendTarget', {
      port: 80,
      targets: [frontendService.loadBalancerTarget({ containerName: 'NexusFrontend', containerPort: 3000 })],
      protocol: elbv2.ApplicationProtocol.HTTP,
      healthCheck: { path: '/' },
    });

    // Rule: Route /api/* to Backend
    httpsListener.addTargets('BackendTarget', {
      priority: 10,
      conditions: [elbv2.ListenerCondition.pathPatterns(['/api/*'])],
      port: 80,
      targets: [backendService.loadBalancerTarget({ containerName: 'NexusApi', containerPort: 8000 })],
      protocol: elbv2.ApplicationProtocol.HTTP,
      healthCheck: { path: '/' }, // Backend health check
    });

    // Optional: HTTP to HTTPS redirect listener
    alb.addListener('HttpRedirectListener', {
      port: 80,
      open: true,
      defaultAction: elbv2.ListenerAction.redirect({ protocol: 'HTTPS', port: '443' })
    });

    // ── CloudFront Distribution ──
    // CloudFront uses the ALB as a dynamic origin.
    const albOrigin = new origins.LoadBalancerV2Origin(alb, {
      protocolPolicy: cloudfront.OriginProtocolPolicy.HTTPS_ONLY,
    });

    const distribution = new cloudfront.Distribution(this, 'NexusDistribution', {
      defaultBehavior: {
        origin: albOrigin,
        // SSR / dynamic requests should not be cached. Pass all headers, cookies, query strings.
        cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
        originRequestPolicy: cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
      },
      additionalBehaviors: {
        // Cache static Next.js assets aggressively
        '/_next/static/*': {
          origin: albOrigin,
          cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
          viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
        },
        // Explicit behavior for API routes: caching strictly disabled
        '/api/*': {
          origin: albOrigin,
          cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
          originRequestPolicy: cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
          viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
        }
      }
    });

    // ── Monitoring (CloudWatch Alarms) ──
    const alertTopic = new sns.Topic(this, 'NexusAlerts');
    
    const cpuAlarm = new cloudwatch.Alarm(this, 'BackendCpuAlarm', {
      metric: backendService.metricCpuUtilization(),
      threshold: 70,
      evaluationPeriods: 5,
      datapointsToAlarm: 5,
    });
    cpuAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(alertTopic));

    // ── Outputs ──
    new cdk.CfnOutput(this, 'AlbUrl', { value: alb.loadBalancerDnsName });
    new cdk.CfnOutput(this, 'CloudFrontUrl', { value: distribution.distributionDomainName });
    new cdk.CfnOutput(this, 'DocumentBucketName', { value: docBucket.bucketName });
  }
}
