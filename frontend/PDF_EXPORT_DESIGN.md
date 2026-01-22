# Nexus Career AI - ATS-Friendly PDF Export Design

## 1. The Golden Rule: "Boring is Best"
For ATS (Applicant Tracking Systems), creativity is the enemy. Complex layouts, graphics, and non-standard fonts confuse parsers, leading to rejected applications. Our export system prioritizes **machine readability** above all else.

## 2. Layout Strategy

### 2.1 Single Column (Recommended)
*   **Why:** Safest for parsing. ATS parsers read left-to-right, top-to-bottom.
*   **Behavior:** Multi-column layouts often get garbled (e.g., combining text from column A and B into a single nonsensical sentence).
*   **Implementation:** A linear flow: Contact Info -> Summary -> Experience -> Skills -> Education.

### 2.2 Minimalist Multi-Column (Optional / Risky)
*   If used, it must be strictly defined (e.g., a small sidebar for Contact/Skills).
*   **Technical Constraint:** Must use accessible tagging structure so screen readers (and robots) know the reading order.

## 3. Typography & Styling

### 3.1 Fonts
*   **Safe List:** Arial, Helvetica, Roboto, Open Sans, Georgia, Times New Roman.
*   **Size:**
    *   Name: 24pt+
    *   Headers: 14-16pt (Bold)
    *   Body: 10-12pt
*   **Line Height:** 1.2 - 1.5 (Ensure lines don't touch).

### 3.2 Elements to AVOID
*   **Icons:** Do not use icons for "Phone" or "Email". Use text labels (e.g., "Phone: ...").
*   **Graphics/Charts:** Skill bars (e.g., "Python: 80%") are unreadable by ATS and subjective. Use text lists instead.
*   **Tables:** Avoid unless absolutely necessary; they often break parsing logic.
*   **Headers/Footers:** Some older ATS systems ignore content in PDF Header/Footer regions. Keep critical info in the main body.

## 4. Structural Requirements

### 4.1 Standard Section Headings
Parsers look for specific keywords to identify sections. We must use standard nomenclature:
*   ✅ "Work Experience", "Professional Experience"
*   ❌ "My Journey", "Where I've Been"
*   ✅ "Skills", "Technical Skills"
*   ❌ "Toolbox", "Superpowers"

### 4.2 Date Formats
*   Use `Month Year` (e.g., "June 2020") or `MM/YYYY` (e.g., "06/2020").
*   Avoid "Summer 2020" or just "2020" (ambiguous for calculating Years of Experience).

## 5. Technical Implementation (React-PDF)

We will use `@react-pdf/renderer` in the Next.js frontend to generate the PDF client-side (or server-side).

### 5.1 Document Structure
```jsx
<Document>
  <Page size="A4" style={styles.page}>
    <View style={styles.section}>
      <Text style={styles.header}>John Doe</Text>
      <Text style={styles.contact}>john@example.com | (555) 123-4567</Text>
    </View>
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>Experience</Text>
      {experiences.map(exp => (
        <View key={exp.id}>
          <Text style={styles.jobTitle}>{exp.title} at {exp.company}</Text>
          <Text style={styles.dates}>{exp.startDate} - {exp.endDate}</Text>
          <View style={styles.bulletPoints}>
            {exp.bullets.map(b => <Text>• {b}</Text>)}
          </View>
        </View>
      ))}
    </View>
  </Page>
</Document>
```

### 5.2 Metadata
*   Ensure the PDF metadata (Properties -> Title/Author) is set correctly.
*   File name: `FirstName_LastName_Resume.pdf`.

## 6. Verification
*   **Text Selection Test:** If you can't select the text in the PDF, the ATS can't read it. (We must export as text, not image).
*   **Plain Text Export:** The system should also offer a `.txt` export option as a fallback for ultra-legacy systems.
