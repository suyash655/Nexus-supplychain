#!/usr/bin/env python3
"""
Convert markdown file to DOCX format
"""
import re
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from pathlib import Path

def convert_md_to_docx(md_file, output_file):
    """Convert markdown file to DOCX"""
    
    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create document
    doc = Document()
    
    # Parse markdown and add to document
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Handle headings
        if line.startswith('# '):
            heading_text = line[2:].strip()
            p = doc.add_heading(heading_text, level=1)
            p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        elif line.startswith('## '):
            p = doc.add_heading(line[3:].strip(), level=2)
        elif line.startswith('### '):
            p = doc.add_heading(line[4:].strip(), level=3)
        elif line.startswith('#### '):
            p = doc.add_heading(line[5:].strip(), level=4)
        
        # Handle code blocks
        elif line.startswith('```'):
            # Collect code block
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            code_text = '\n'.join(code_lines).strip()
            p = doc.add_paragraph(code_text, style='List Bullet')
            p.style = 'Normal'
            # Apply monospace formatting
            for run in p.runs:
                run.font.name = 'Courier New'
                run.font.size = Pt(9)
        
        # Handle horizontal rules
        elif line.startswith('---') or line.startswith('***'):
            doc.add_paragraph('')
        
        # Handle bullet points
        elif line.startswith('- ') or line.startswith('* '):
            bullet_text = re.sub(r'^[-*]\s+', '', line).strip()
            # Handle inline formatting with bold and italics
            bullet_text = format_inline_text(bullet_text)
            doc.add_paragraph(bullet_text, style='List Bullet')
        
        # Handle numbered list
        elif re.match(r'^\d+\.\s+', line):
            list_text = re.sub(r'^\d+\.\s+', '', line).strip()
            list_text = format_inline_text(list_text)
            doc.add_paragraph(list_text, style='List Number')
        
        # Handle tables
        elif line.strip().startswith('|'):
            # Collect table rows
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = [cell.strip() for cell in lines[i].split('|')[1:-1]]
                table_rows.append(row)
                i += 1
            i -= 1
            
            if table_rows:
                # Create table
                table = doc.add_table(rows=len(table_rows), cols=len(table_rows[0]))
                table.style = 'Light Grid Accent 1'
                
                for row_idx, row_data in enumerate(table_rows):
                    for col_idx, cell_data in enumerate(row_data):
                        cell = table.rows[row_idx].cells[col_idx]
                        # Skip header separator row
                        if not all(c in [':', '-', ' '] for c in cell_data):
                            cell.text = cell_data.strip()
        
        # Handle empty lines
        elif line.strip() == '':
            # Only add paragraph if last paragraph isn't empty
            if doc.paragraphs and doc.paragraphs[-1].text.strip():
                doc.add_paragraph('')
        
        # Regular paragraphs
        else:
            if line.strip():
                formatted_text = format_inline_text(line.strip())
                doc.add_paragraph(formatted_text)
        
        i += 1
    
    # Save document
    doc.save(output_file)
    print(f"✓ Successfully converted to: {output_file}")

def format_inline_text(text):
    """Handle inline markdown formatting (bold, italic, code)"""
    # Bold: **text** or __text__
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    
    # Italic: *text* or _text_
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    
    # Code: `text`
    text = re.sub(r'`(.*?)`', r'\1', text)
    
    # Links: [text](url)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    
    return text

if __name__ == '__main__':
    md_file = r'd:\supex1\PROJECT_EXPLANATION_FOR_PROFESSOR.md'
    output_file = r'd:\supex1\SynChain_2.0_Project_Explanation.docx'
    
    print(f"Converting {md_file} to DOCX...")
    convert_md_to_docx(md_file, output_file)
