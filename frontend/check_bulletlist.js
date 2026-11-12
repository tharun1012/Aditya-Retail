const { StarterKit } = require('@tiptap/starter-kit');
const inst = StarterKit.configure();
const exts = inst.config.addExtensions.call(inst);
const bulletList = exts.find(e => e.name === 'bulletList');
console.log('bulletList extension found:', !!bulletList);
console.log('addCommands defined:', typeof bulletList?.config?.addCommands);
if (bulletList?.config?.addCommands) {
  const commands = bulletList.config.addCommands.call(bulletList);
  console.log('bulletList commands:', Object.keys(commands));
}
