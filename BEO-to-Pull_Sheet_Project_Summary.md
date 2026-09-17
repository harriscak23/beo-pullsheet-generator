Here’s a summary of everything we discussed about the project:

### Project: BEO-to-Pull Sheet Automation System

- You work on campus for a **university catering department**.
- The catering workflow involves two main documents:
  - **BEO (Banquet Event Order):** A digital/online PDF containing information about an event, including food, drinks, guest count, and other event details.
  - **Pull Sheet / White Sheet:** A fixed form listing the equipment and supplies workers need to bring, such as tongs, cups, plates, and linens. Workers currently fill in the quantities by hand.
- Your goal is to **automate the creation of the pull sheet from the BEO**, reducing repetitive manual work and potential errors.

### Current Implementation

- **Input:** Digital BEO PDF.
- **PDF processing:** You are using **Python and pdfplumber** to extract information from the BEO.
- **OCR:** Not necessary because BEOs are always digital PDFs with machine-readable text.
- **Processing:** Extracted BEO information is converted into structured data that the application can process.
- **Rules:** You currently use a **rule-based system**, with the rules stored in a **JSON file**.
- Example:
  - Coffee → coffee cups
  - Buffet → chafers/tongs
  - Guest count → determine quantities
- **Output:** A completed **Microsoft Word (.docx)** pull sheet that can be reviewed and printed.

### Rule-Based vs. Machine Learning

We discussed that a rule-based approach makes sense as the starting point because many catering decisions are deterministic and can be represented as explicit rules.

However, you eventually want to add **machine learning** because experienced catering workers may make decisions based on special cases or patterns that are difficult to express with simple rules.

The planned architecture is:

```text
BEO PDF
   ↓
pdfplumber
   ↓
Structured Event Data
   ↓
Rule Engine ──────┐
                  ├──→ Pull Sheet
ML Model ─────────┘
   ↓
Human Review
   ↓
Print
```

The ML component is **not implemented yet**. Before building it, you need to clean and digitize historical data.

### Historical Data Challenge

- Historical pull sheets are **handwritten**.
- The pull sheet itself is a **fixed form with a predefined list of items and handwritten quantities**.
- Because the layout is fixed, extracting historical data should be more manageable than processing completely free-form handwritten documents.
- You need to determine:
  - How many historical BEO/pull-sheet pairs exist.
  - How consistently workers fill out the sheets.
  - How many special cases exist.
  - How consistent item names and quantities are.
- The cleaned historical BEO/pull-sheet pairs could eventually become the training dataset for the ML model.

### Future Database

Currently:

```text
rules.json
```

You plan to eventually move the rules into a **database**.

The database would make it easier to:
- Manage a growing number of rules.
- Update rules without modifying application code.
- Potentially allow supervisors to manage rules through an interface.
- Store historical information that can later support ML.

### Deployment

We discussed several possible deployment options:

1. **Web application** — recommended long-term approach.
2. **Desktop application** — potentially useful for an initial prototype.
3. **Excel-based tool** — possible if catering already relies heavily on Excel.
4. **Integration with existing catering software** — potentially ideal but likely more difficult because it depends on APIs and university IT/vendor access.

For the first version, a **standalone web application** would likely be the best direction:

```text
Upload BEO
   ↓
Generate Pull Sheet
   ↓
Employee Reviews/Edits
   ↓
Print
```

This avoids needing to integrate directly with the university's existing catering software.

### Project Name

The name we settled on as the strongest resume option was:

**BEO-to-Pull Sheet Automation System**

Other names considered included:
- Catering Pull Sheet Automation System
- BEO Pull Sheet Generator
- Catering Event Supply Automation System
- Intelligent Catering Pull Sheet Generator

### Resume Version

The current resume description is:

**BEO-to-Pull Sheet Automation System** | Python, pdfplumber, JSON, python-docx

- Developed a Python application that extracts event details from digital **Banquet Event Order (BEO) PDFs** using pdfplumber and automatically generates formatted pull sheets in **.docx**.
- Implemented a **JSON-based rule engine** to determine required catering equipment, supplies, and quantities based on guest count, menu items, beverages, and service style.
- Designed a roadmap to migrate rules to a **database** and integrate **machine learning** using historical BEO and pull-sheet data to identify special cases and improve predictions.

### Overall Project Direction

The key idea is **not to force ML into the project immediately**. The current plan is:

**Rules → collect/clean data → database → ML → hybrid system**

The rule-based system gives you a working baseline now. Historical BEOs and handwritten pull sheets provide the data needed to discover special cases and eventually train an ML model. The final system would combine deterministic business rules with ML predictions and keep a **human review step** before the pull sheet is printed.
