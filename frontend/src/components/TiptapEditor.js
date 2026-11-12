import React, { useRef, useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import ImageExtension from '@tiptap/extension-image';
import HighlightExtension from '@tiptap/extension-highlight';
import TextAlignExtension from '@tiptap/extension-text-align';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import { Table } from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import {
  Bold, Italic, Underline as UnderlineIcon, Strikethrough, Highlighter,
  List, ListOrdered, ListChecks, Link as LinkIcon, Image as ImageIcon,
  AlignLeft, AlignCenter, AlignRight, AlignJustify, Table as TableIcon,
  Undo2, Redo2, ChevronDown
} from 'lucide-react';
import './TiptapEditor.css';
const HEADING_LEVELS = [
  { level: 0, label: 'Paragraph' },
  { level: 1, label: 'Heading 1' },
  { level: 2, label: 'Heading 2' },
  { level: 3, label: 'Heading 3' },
  { level: 4, label: 'Heading 4' }
];

const LIST_TYPES = [
  { id: 'bulletList', label: 'Bullet List', icon: List },
  { id: 'orderedList', label: 'Ordered List', icon: ListOrdered },
  { id: 'taskList', label: 'Task List', icon: ListChecks }
];

const TiptapEditor = ({ value, onChange, backendUrl, authToken, placeholder = 'Write your blog content here…' }) => {
  const fileInputRef = useRef(null);
  const [headingMenuOpen, setHeadingMenuOpen] = useState(false);
  const [listMenuOpen, setListMenuOpen] = useState(false);

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        link: { openOnClick: false, autolink: true }
      }),
      HighlightExtension,
      TextAlignExtension.configure({ types: ['heading', 'paragraph'] }),
      TaskList,
      TaskItem.configure({ nested: true }),
      Table.configure({ resizable: true }),
      TableRow,
      TableHeader,
      TableCell,
      ImageExtension.configure({ HTMLAttributes: { class: 'rounded-lg max-w-full my-4' } })
    ],
    content: value || '',
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
    editorProps: {
      attributes: {
        class: 'prose max-w-none min-h-[24rem] p-4 border-x border-b rounded-b-lg focus:outline-none'
      }
    }
  });

  const handleImageButtonClick = () => fileInputRef.current?.click();

  const handleImageSelected = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = '';
    if (!file || !editor) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(`${backendUrl}/api/upload/upload-image`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${authToken}` },
        body: formData
      });
      const data = await res.json();
      if (data.status === 'success' && data.image_url) {
        editor.chain().focus().setImage({ src: data.image_url }).run();
      } else {
        alert('Image upload failed');
      }
    } catch (err) {
      console.error('Image upload error:', err);
      alert('Image upload failed');
    }
  };

  const addLink = () => {
    const url = window.prompt('Enter URL (use /path for internal pages):');
    if (url) editor.chain().focus().setLink({ href: url }).run();
  };

  const insertTable = () => {
    editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run();
  };

  const setHeading = (level) => {
    if (level === 0) editor.chain().focus().setParagraph().run();
    else editor.chain().focus().toggleHeading({ level }).run();
    setHeadingMenuOpen(false);
  };

  const toggleList = (id) => {
    if (id === 'bulletList') editor.chain().focus().toggleBulletList().run();
    if (id === 'orderedList') editor.chain().focus().toggleOrderedList().run();
    if (id === 'taskList') editor.chain().focus().toggleTaskList().run();
    setListMenuOpen(false);
  };

  if (!editor) return null;

  const currentHeading = HEADING_LEVELS.find(h =>
    h.level === 0 ? !editor.isActive('heading') : editor.isActive('heading', { level: h.level })
  ) || HEADING_LEVELS[0];

  const currentList = LIST_TYPES.find(l => editor.isActive(l.id));

  const ToolbarButton = ({ onClick, active, children, title, disabled }) => (
    <button
      type="button"
      onMouseDown={(e) => { e.preventDefault(); if (!disabled) onClick(); }}
      title={title}
      disabled={disabled}
      className={`p-2 rounded hover:bg-gray-100 transition-colors disabled:opacity-30 disabled:cursor-not-allowed ${active ? 'bg-gray-200 text-amber-700' : 'text-gray-700'}`}
    >
      {children}
    </button>
  );

  return (
    <div>
      <div className="flex flex-wrap items-center gap-1 p-2 border rounded-t-lg bg-gray-50 relative">
        <ToolbarButton title="Undo" onClick={() => editor.chain().focus().undo().run()} disabled={!editor.can().undo()}>
          <Undo2 className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton title="Redo" onClick={() => editor.chain().focus().redo().run()} disabled={!editor.can().redo()}>
          <Redo2 className="w-4 h-4" />
        </ToolbarButton>

        <div className="w-px h-6 bg-gray-300 mx-1" />

        <div className="relative">
          <button
            type="button"
            onMouseDown={(e) => { e.preventDefault(); setHeadingMenuOpen(o => !o); setListMenuOpen(false); }}
            className="flex items-center gap-1 px-2 py-2 rounded hover:bg-gray-100 text-sm text-gray-700"
          >
            {currentHeading.label} <ChevronDown className="w-3 h-3" />
          </button>
          {headingMenuOpen && (
            <div className="absolute top-full left-0 mt-1 w-36 bg-white rounded-lg shadow-xl border z-20">
              {HEADING_LEVELS.map(h => (
                <button
                  key={h.level}
                  type="button"
                  onMouseDown={(e) => { e.preventDefault(); setHeading(h.level); }}
                  className={`w-full text-left px-3 py-2 text-sm hover:bg-amber-50 ${currentHeading.level === h.level ? 'text-amber-700 font-medium' : 'text-gray-700'}`}
                >
                  {h.label}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="relative">
          <button
            type="button"
            onMouseDown={(e) => { e.preventDefault(); setListMenuOpen(o => !o); setHeadingMenuOpen(false); }}
            className="flex items-center gap-1 p-2 rounded hover:bg-gray-100 text-gray-700"
            title="Lists"
          >
            {currentList ? <currentList.icon className="w-4 h-4" /> : <List className="w-4 h-4" />}
            <ChevronDown className="w-3 h-3" />
          </button>
          {listMenuOpen && (
            <div className="absolute top-full left-0 mt-1 w-40 bg-white rounded-lg shadow-xl border z-20">
              {LIST_TYPES.map(l => (
                <button
                  key={l.id}
                  type="button"
                  onMouseDown={(e) => { e.preventDefault(); toggleList(l.id); }}
                  className={`w-full flex items-center gap-2 text-left px-3 py-2 text-sm hover:bg-amber-50 ${editor.isActive(l.id) ? 'text-amber-700 font-medium' : 'text-gray-700'}`}
                >
                  <l.icon className="w-4 h-4" /> {l.label}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="w-px h-6 bg-gray-300 mx-1" />

        <ToolbarButton title="Bold" onClick={() => editor.chain().focus().toggleBold().run()} active={editor.isActive('bold')}>
          <Bold className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton title="Italic" onClick={() => editor.chain().focus().toggleItalic().run()} active={editor.isActive('italic')}>
          <Italic className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton title="Strikethrough" onClick={() => editor.chain().focus().toggleStrike().run()} active={editor.isActive('strike')}>
          <Strikethrough className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton title="Underline" onClick={() => editor.chain().focus().toggleUnderline().run()} active={editor.isActive('underline')}>
          <UnderlineIcon className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton title="Highlight" onClick={() => editor.chain().focus().toggleHighlight().run()} active={editor.isActive('highlight')}>
          <Highlighter className="w-4 h-4" />
        </ToolbarButton>

        <div className="w-px h-6 bg-gray-300 mx-1" />

        <ToolbarButton title="Align Left" onClick={() => editor.chain().focus().setTextAlign('left').run()} active={editor.isActive({ textAlign: 'left' })}>
          <AlignLeft className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton title="Align Center" onClick={() => editor.chain().focus().setTextAlign('center').run()} active={editor.isActive({ textAlign: 'center' })}>
          <AlignCenter className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton title="Align Right" onClick={() => editor.chain().focus().setTextAlign('right').run()} active={editor.isActive({ textAlign: 'right' })}>
          <AlignRight className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton title="Justify" onClick={() => editor.chain().focus().setTextAlign('justify').run()} active={editor.isActive({ textAlign: 'justify' })}>
          <AlignJustify className="w-4 h-4" />
        </ToolbarButton>

        <div className="w-px h-6 bg-gray-300 mx-1" />

        <ToolbarButton title="Insert Table" onClick={insertTable}>
          <TableIcon className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton title="Insert Link" onClick={addLink} active={editor.isActive('link')}>
          <LinkIcon className="w-4 h-4" />
        </ToolbarButton>
        <ToolbarButton title="Insert Image" onClick={handleImageButtonClick}>
          <ImageIcon className="w-4 h-4" />
        </ToolbarButton>
        <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleImageSelected} />
      </div>
      <EditorContent editor={editor} placeholder={placeholder} />
    </div>
  );
};

export default TiptapEditor;
