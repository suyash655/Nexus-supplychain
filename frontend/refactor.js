const fs = require('fs');
const path = require('path');

const baseDir = path.join(__dirname, 'app');

function getFiles(dir, files = []) {
  const list = fs.readdirSync(dir);
  for (const file of list) {
    const res = path.resolve(dir, file);
    if (fs.statSync(res).isDirectory()) {
      getFiles(res, files);
    } else if (res.endsWith('.tsx') || res.endsWith('.ts')) {
      files.push(res);
    }
  }
  return files;
}

const replacements = [
  // Charts
  { old: 'components/Charts', new: 'components/charts/Charts' },
];

const files = getFiles(baseDir);
let updatedCount = 0;

for (const file of files) {
  let content = fs.readFileSync(file, 'utf8');
  let changed = false;
  
  for (const { old: o, new: n } of replacements) {
    const regex = new RegExp(`(["'])(.*?)${o}(["'])`, 'g');
    if (regex.test(content)) {
      content = content.replace(regex, `$1$2${n}$3`);
      changed = true;
    }
  }
  
  if (changed) {
    fs.writeFileSync(file, content, 'utf8');
    updatedCount++;
    console.log(`Updated imports in ${path.relative(baseDir, file)}`);
  }
}

console.log(`Updated ${updatedCount} files.`);
