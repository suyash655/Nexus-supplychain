"use client";

import { useRef, useEffect, useState, ReactNode } from "react";
import { motion, useInView, useScroll, useTransform } from "framer-motion";

/**
 * AnimatedSection — Scroll-triggered reveal wrapper.
 * Every major section uses this for the "wow" factor.
 */
export function AnimatedSection({
  children,
  className = "",
  delay = 0,
  direction = "up",
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
  direction?: "up" | "down" | "left" | "right";
}) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-80px" });

  const offsets = {
    up: { x: 0, y: 40 },
    down: { x: 0, y: -40 },
    left: { x: 40, y: 0 },
    right: { x: -40, y: 0 },
  };

  return (
    <motion.div
      ref={ref}
      className={className}
      initial={{ opacity: 0, x: offsets[direction].x, y: offsets[direction].y }}
      animate={isInView ? { opacity: 1, x: 0, y: 0 } : {}}
      transition={{ duration: 0.6, ease: "easeOut", delay }}
    >
      {children}
    </motion.div>
  );
}

/**
 * StaggerGrid — Children animate in one by one with staggered timing.
 */
export function StaggerGrid({
  children,
  className = "",
  style,
  stagger = 0.08,
}: {
  children: ReactNode;
  className?: string;
  style?: React.CSSProperties;
  stagger?: number;
}) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-60px" });

  return (
    <motion.div
      ref={ref}
      className={className}
      style={style}
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
      variants={{
        hidden: {},
        visible: { transition: { staggerChildren: stagger } },
      }}
    >
      {children}
    </motion.div>
  );
}

/**
 * StaggerItem — Individual item inside a StaggerGrid.
 */
export function StaggerItem({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <motion.div
      className={className}
      variants={{
        hidden: { opacity: 0, y: 20, scale: 0.97 },
        visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.4, ease: "easeOut" } },
      }}
    >
      {children}
    </motion.div>
  );
}

/**
 * ScrollProgress — Thin progress bar at top of viewport.
 */
export function ScrollProgress() {
  const { scrollYProgress } = useScroll();
  const scaleX = useTransform(scrollYProgress, [0, 1], [0, 1]);

  return (
    <motion.div
      className="scroll-progress"
      style={{ scaleX, transformOrigin: "left" }}
    />
  );
}

/**
 * ParallaxHeader — Subtle parallax effect on header sections.
 */
export function ParallaxHeader({
  children,
  className = "",
  speed = 0.3,
}: {
  children: ReactNode;
  className?: string;
  speed?: number;
}) {
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 300], [0, -40 * speed]);

  return (
    <motion.div className={className} style={{ y }}>
      {children}
    </motion.div>
  );
}

/**
 * HoverCard — Card with spring hover animation.
 */
export function HoverCard({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <motion.div
      className={`card ${className}`}
      whileHover={{ y: -8, scale: 1.01 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
    >
      {children}
    </motion.div>
  );
}

/**
 * AnimatedIcon — Icon with hover scale + rotate.
 */
export function AnimatedIcon({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <motion.div
      className={className}
      whileHover={{ scale: 1.3, rotate: 8 }}
      transition={{ type: "spring", stiffness: 400 }}
      style={{ display: "inline-flex" }}
    >
      {children}
    </motion.div>
  );
}
