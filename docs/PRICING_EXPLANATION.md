# 💰 Pricing Calculation Explanation - Jasmin Catering AI Agent

## How Pricing Works

### 1. **Pricing Source**
The pricing information comes from **TWO sources**:

#### A. RAG Documents (Azure AI Search)
The file `knowledge-base/documents/pricing-structure.md` contains comprehensive pricing:
- **Basis Package**: €25-35 per person
- **Standard Package**: €35-45 per person
- **Premium Package**: €50-70 per person
- All discounts and surcharges

#### B. System Prompt (Embedded Knowledge)
The AI assistant has pricing rules embedded directly in its system prompt:
```python
PREISSTRUKTUR & PAKETE:
**Basis-Paket (25-35€/Person):** 
**Standard-Paket (35-45€/Person):** 
**Premium-Paket (50-70€/Person):** 

RABATTE & ZUSCHLÄGE:
- Werktags (Mo-Do): 10% Rabatt
- Große Gruppen 50+: 10% Rabatt
- Gemeinnützige Organisationen: 10% Rabatt
- Wochenende: +10% Zuschlag
- Eilauftrag (<48h): +25% Zuschlag
```

### 2. **Calculation Process**

The AI calculates prices using this logic:

1. **Base Price Selection**
   - Determines package tier based on customer requirements
   - Uses the middle of the range (e.g., €30 for Basis 25-35€)

2. **Apply Group Size**
   - Multiplies base price by number of guests

3. **Apply Discounts/Surcharges**
   - Weekday events: -10%
   - Large groups (50+): -10%
   - Nonprofit organizations: -10%
   - Rush orders (<48h): +25%
   - Weekend events: +10%
   - Summer/holidays: +15-20%

4. **Add Extras**
   - Delivery fees (based on distance)
   - Special services (Arabic coffee, etc.)

### 3. **Example Calculations**

#### Email 1: Corporate Event (75 people, Thursday)
- Base: Standard Package €40/person
- 75 × €40 = €3,000
- Weekday discount: -10% = €2,700
- Large group discount: -10% = €2,430

#### Email 2: Nonprofit Gala (120 people)
- Base: Standard Package €40/person
- 120 × €40 = €4,800
- Nonprofit discount: -10% = €4,320
- Large group discount: -10% = €3,888

#### Email 3: Rush Order (25 people, tomorrow)
- Base: Basis Package €30/person
- 25 × €30 = €750
- Rush charge: +25% = €937.50
- Delivery fee: +€50 = €987.50

#### Email 4: Premium Wedding (200 people, Saturday, Summer)
- Base: Premium Package €60/person
- 200 × €60 = €12,000
- Weekend surcharge: +10% = €13,200
- Summer premium: +15% = €15,180
- Large group discount: -15% = €12,903
- Delivery to Potsdam: +€100 = €13,003

#### Email 5: Weekly Catering (30 people, Wednesdays)
- Base: Basis Package €25/person (volume pricing)
- 30 × €25 = €750
- Weekday discount: -10% = €675
- Potential loyalty discount after 3 bookings: -5%

### 4. **Why You See Prices**

You see prices because:

1. **RAG Documents Include Pricing**: The `pricing-structure.md` file uploaded to Azure AI Search contains complete pricing information

2. **System Prompt Has Pricing**: The AI assistant's configuration includes pricing rules directly

3. **Business Requirement**: The assistant is instructed to "ALWAYS create three detailed quote options" with specific pricing

4. **Transparency**: German business culture values transparent pricing, so the AI provides clear cost breakdowns

### 5. **Pricing Accuracy**

The AI's pricing is:
- **Consistent**: Uses the same rules for similar requests
- **Contextual**: Applies appropriate discounts/surcharges
- **Transparent**: Shows how prices are calculated
- **Flexible**: Provides three options (Basis/Standard/Premium)

## Summary

The pricing you see is NOT random or made up. It comes from:
1. ✅ Structured data in RAG documents
2. ✅ Business rules in the system prompt
3. ✅ Logical calculations based on request details
4. ✅ Consistent application of discounts/surcharges

This ensures customers receive accurate, fair, and transparent pricing that reflects Jasmin Catering's actual business model.