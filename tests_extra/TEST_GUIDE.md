# Comprehensive Test Suite for FAQ-RAG System

## Περιγραφή

Αυτό το script είναι ένα ολοκληρωμένο test suite προσαρμοσμένο για το CloudSphere FAQ-RAG σύστημά σας που τρέχει με FastAPI και Ollama.

## Πώς να το τρέξετε

### 1. Ξεκινήστε το API server
```bash
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

### 2. Τρέξτε το comprehensive test
```bash
python comprehensive_test_clean.py
```

## Τι τεστάρει το script

### 🔧 Basic Functionality Tests
- Τεστάρει βασικές ερωτήσεις από το CloudSphere knowledge base
- Ελέγχει αν οι απαντήσεις περιέχουν σχετικές λέξεις-κλειδιά
- Μετράει response times

### 🧪 Edge Cases Tests
- Κενές ερωτήσεις
- Πολύ μικρές/μεγάλες ερωτήσεις  
- Ερωτήσεις εκτός γνωστικού πεδίου
- Μη-αγγλικές ερωτήσεις
- Ειδικούς χαρακτήρες

### 📋 History Endpoint Tests
- Τεστάρει το `/history` endpoint
- Ελέγχει limit parameters
- Επαληθεύει την structure των αποτελεσμάτων

### ⚡ Performance Analysis
- Μετράει average response times
- Κατηγοριοποιεί την απόδοση (Fast/Medium/Slow)
- Τρέχει multiple runs για ακρίβεια

### 📚 Knowledge Coverage Tests
- Τεστάρει διαφορετικές περιοχές γνώσης:
  - Pricing & Billing
  - Security & Compliance  
  - Technical Support
  - API & Integration
  - Account Management

## Αποτελέσματα

Το script παρέχει:
- ✅ **Detailed test results** για κάθε κατηγορία
- 📊 **Performance metrics** και distribution analysis  
- 🎯 **Overall System Health Score** (0-100%)
- 💡 **Recommendations** για βελτιώσεις

## Παραδείγματα ερωτήσεων που τεστάρει

### CloudSphere-specific questions:
- "What is CloudSphere Platform and who is it for?"
- "How much does the Professional tier cost?" 
- "Do you offer a free trial?"
- "I forgot my password, how can I reset it?"
- "What industry compliance certifications do you have?"
- "What are the API rate limits?"

### Edge cases:
- Empty questions, very long questions
- Non-English: "Τι είναι το CloudSphere Platform;"
- Out of scope: "What's the weather today?"

## Συμβουλές χρήσης

1. **Βεβαιωθείτε ότι το Ollama τρέχει** με το Mistral model
2. **Περιμένετε** - το πρώτο request μπορεί να είναι αργό λόγω model loading
3. **Παρακολουθήστε τα logs** του API για errors
4. **Τρέξτε το script σε διαστήματα** για consistency testing

## Customization

Μπορείτε εύκολα να:
- Προσθέσετε νέες ερωτήσεις στο `test_questions` array
- Αλλάξετε τα expected keywords
- Προσαρμόσετε τα timeouts
- Προσθέσετε νέες κατηγορίες coverage tests

## Troubleshooting

**API Connection Issues:**
- Ελέγξτε ότι το API τρέχει στο localhost:8000
- Βεβαιωθείτε ότι το Ollama service είναι ενεργό

**Slow Performance:**
- Το Mistral model μπορεί να θέλει χρόνο για την πρώτη φόρτωση
- Ελέγξτε τους system resources

**Test Failures:**
- Κοιτάξτε τα API logs για errors
- Ελέγξτε τη knowledge base για completeness
