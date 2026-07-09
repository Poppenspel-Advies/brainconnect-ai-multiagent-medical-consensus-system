from fpdf import FPDF

class MedicalPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, 'MEDICAL RECORD - CONFIDENTIAL', align='C', new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_fill_color(230, 240, 250)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)
    
    def section_body(self, text):
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 5, text)
        self.ln(3)

pdf = MedicalPDF()
pdf.alias_nb_pages()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=20)

# Patient Demographics
pdf.section_title('PATIENT DEMOGRAPHICS')
pdf.section_body(
    'Patient Name: James Robert Anderson\n'
    'Date of Birth: March 15, 1962 (Age: 62 years)\n'
    'Sex: Male\n'
    'MRN: 8472910\n'
    'Date of Encounter: July 5, 2026\n'
    'Encounter Type: Emergency Department Visit\n'
    'Attending Physician: Dr. Sarah Mitchell, MD\n'
    'Primary Care Provider: Dr. Michael Chen, MD\n'
    'Insurance: Medicare Part A & B / Supplemental Plan G'
)

# Chief Complaint
pdf.section_title('CHIEF COMPLAINT')
pdf.section_body(
    'Acute onset chest pressure with radiation to left arm and jaw, '
    'associated with shortness of breath and diaphoresis, duration 45 minutes prior to arrival.'
)

# History of Present Illness
pdf.section_title('HISTORY OF PRESENT ILLNESS')
pdf.section_body(
    'Mr. Anderson is a 62-year-old male who presents to the Emergency Department '
    'with acute onset of substernal chest pressure beginning approximately 45 minutes '
    'prior to arrival while at rest watching television. The pain is described as a '
    '"heavy pressure" rated 8/10 in severity, radiating to the left arm, neck, and jaw. '
    'Associated symptoms include shortness of breath, profuse diaphoresis, nausea, '
    'and a sense of impending doom. He denies palpitations, syncope, or fever. '
    'He took one sublingual nitroglycerin tablet (0.4 mg) at home with minimal relief. '
    'EMS obtained ECG en route showing ST-segment elevation in leads II, III, and aVF. '
    'Patient received aspirin 325 mg chewed, nitroglycerin paste, and morphine 2 mg IV '
    'by EMS with partial pain relief (now 4/10). No prior similar episodes. '
    'No recent trauma, surgery, or immobilization. No recent travel.'
)

# Past Medical History
pdf.section_title('PAST MEDICAL HISTORY')
pdf.section_body(
    '1. Hypertension (diagnosed 2010) - on lisinopril 20 mg daily\n'
    '2. Type 2 Diabetes Mellitus (diagnosed 2014) - HbA1c 7.2% (last checked 2025-11), on metformin 1000 mg BID\n'
    '3. Hyperlipidemia (diagnosed 2012) - on atorvastatin 40 mg daily\n'
    '4. Chronic Kidney Disease Stage 3a (eGFR 52 mL/min/1.73m2) - nephrology follow-up annually\n'
    '5. Obstructive Sleep Apnea - CPAP compliant\n'
    '6. Remote history of tobacco use - quit 2015 (30 pack-year history)\n'
    '7. No prior MI, PCI, CABG, stroke, or peripheral artery disease\n'
    '8. No known coronary artery disease previously documented'
)

# Surgical History
pdf.section_title('SURGICAL HISTORY')
pdf.section_body(
    '1. Laparoscopic cholecystectomy (2018) - uncomplicated\n'
    '2. Left knee arthroscopy for meniscal tear (2005)\n'
    '3. No prior cardiac procedures'
)

# Medications
pdf.section_title('CURRENT MEDICATIONS')
pdf.section_body(
    '1. Lisinopril 20 mg PO daily\n'
    '2. Metformin 1000 mg PO BID\n'
    '3. Atorvastatin 40 mg PO daily\n'
    '4. Aspirin 81 mg PO daily (taken this morning prior to event)\n'
    '5. Tamsulosin 0.4 mg PO daily (for BPH)\n'
    '6. Vitamin D3 2000 IU PO daily\n'
    '7. Omeprazole 20 mg PO daily (PRN for GERD)\n'
    'Allergies: NKDA (No Known Drug Allergies)'
)

# Social History
pdf.section_title('SOCIAL HISTORY')
pdf.section_body(
    'Tobacco: Former smoker, quit 2015 (30 pack-year history)\n'
    'Alcohol: Occasional wine with dinner (2-3 glasses/week)\n'
    'Illicit Drugs: Denies\n'
    'Occupation: Retired mechanical engineer\n'
    'Living Situation: Lives with wife in two-story home\n'
    'Exercise: Daily 30-minute walks, CPAP compliant nightly\n'
    'Diet: Mediterranean-style, sodium-restricted'
)

# Family History
pdf.section_title('FAMILY HISTORY')
pdf.section_body(
    'Father: Deceased age 68 - MI\n'
    'Mother: Deceased age 82 - stroke\n'
    'Brother (age 65): Alive - HTN, hyperlipidemia, status post PCI 2020\n'
    'Sister (age 58): Alive - T2DM\n'
    'Two adult children: Alive and well\n'
    'No family history of sudden cardiac death or cardiomyopathy'
)

# Physical Examination
pdf.section_title('PHYSICAL EXAMINATION')
pdf.section_body(
    'Vital Signs: BP 148/92 mmHg (right arm), HR 98 bpm (regular), '
    'RR 22/min, Temp 98.4 F (36.9 C), SpO2 94% on room air, '
    'improved to 98% on 2L NC\n\n'
    'General: Alert, oriented x3, in moderate distress, diaphoretic\n'
    'HEENT: PERRLA, EOMI, moist mucous membranes, no JVD at 30 degrees\n'
    'Neck: Supple, no carotid bruits, thyroid non-palpable\n'
    'Cardiovascular: Regular rate and rhythm, S1/S2 normal, '
    'S4 present at apex, no murmurs/rubs/gallops, '
    'pulses 2+ bilaterally in carotids, radial, femoral, popliteal, DP/PT\n'
    'Respiratory: Clear to auscultation bilaterally, no wheezes/rhonchi/rales, '
    'good air movement, no increased work of breathing\n'
    'Abdomen: Soft, non-tender, non-distended, BS present x4 quadrants, '
    'no hepatosplenomegaly, no masses\n'
    'Extremities: No edema, calves non-tender, no Homan\'s sign\n'
    'Neurologic: Alert, oriented, CN II-XII grossly intact, '
    'motor/sensory intact, gait not assessed\n'
    'Skin: Diaphoretic, warm, no rash/lesions'
)

# Laboratory Results
pdf.section_title('LABORATORY RESULTS')
pdf.section_body(
    'Troponin I (High Sensitivity): 12.4 ng/mL (ref: <0.04) - ELEVATED\n'
    'Troponin I (repeat at 3 hours): 48.7 ng/mL - RISING\n'
    'CK-MB: 28.5 ng/mL (ref: <6.3) - ELEVATED\n'
    'CBC: WBC 11.2 K/uL, Hgb 13.8 g/dL, Hct 41.2%, Plt 285 K/uL\n'
    'BMP: Na 139, K 4.2, Cl 102, CO2 24, BUN 28, Cr 1.4 (baseline 1.3), '
    'Glucose 186 mg/dL\n'
    'Lipid Panel (fasting from 2025-11): Total 178, LDL 98, HDL 42, TG 190\n'
    'HbA1c (2025-11): 7.2%\n'
    'eGFR: 52 mL/min/1.73m2 (CKD-EPI)\n'
    'BNP: 385 pg/mL (ref: <100) - ELEVATED\n'
    'Coagulation: PT 13.2, INR 1.0, aPTT 28\n'
    'Lactate: 2.1 mmol/L (ref: 0.5-2.0) - SLIGHTLY ELEVATED\n'
    'COVID-19 PCR: Negative\n'
    'Influenza A/B: Negative'
)

# ECG Findings
pdf.section_title('ECG FINDINGS')
pdf.section_body(
    '12-Lead ECG (07:23 AM): Sinus rhythm at 98 bpm. '
    'ST-segment elevation (2-3 mm) in leads II, III, aVF with reciprocal '
    'ST-depression in leads I, aVL, V2-V4. '
    'PR interval 168 ms, QRS 92 ms, QTc 440 ms. '
    'No pathologic Q waves. '
    'Comparison with prior ECG (2025-11): Previous ECG showed normal sinus rhythm, '
    'no ST-T changes.\n\n'
    'Continuous Monitoring: Intermittent PVCs (3-4/min), no sustained arrhythmias.'
)

# Imaging Results
pdf.section_title('IMAGING RESULTS')
pdf.section_body(
    'Chest X-Ray (Portable, 07:35 AM): Heart size at upper limits of normal '
    '(CT ratio 0.52). Mild pulmonary vascular congestion. '
    'No pleural effusions, no consolidation. '
    'Bilateral costophrenic angles clear.\n\n'
    'Bedside Echocardiogram (08:15 AM): LVEF 45-50% (mildly reduced). '
    'Regional wall motion abnormality: Inferior and inferolateral hypokinesis. '
    'No pericardial effusion. RV systolic function normal. '
    'No valvular abnormalities. IVC dilated with <50% collapse.'
)

# Assessment / Working Diagnosis
pdf.section_title('ASSESSMENT / WORKING DIAGNOSIS')
pdf.section_body(
    '1. ST-Elevation Myocardial Infarction (STEMI) - Inferior wall, '
    'Occlusion likely RCA given STE II, III, aVF with reciprocal changes.\n'
    '2. Acute Decompensated Heart Failure (new onset) - Elevated BNP, '
    'pulmonary congestion on CXR, reduced EF with inferior WMA.\n'
    '3. Type 2 Diabetes Mellitus - Suboptimally controlled (HbA1c 7.2%).\n'
    '4. Hypertension - Elevated on presentation (148/92).\n'
    '5. Chronic Kidney Disease Stage 3a - Stable baseline.\n'
    '6. Obstructive Sleep Apnea - On CPAP.\n\n'
    'Plan:\n'
    '1. EMERGENT CARDIAC CATHETERIZATION WITH PCI - Cath lab activated.\n'
    '2. Dual antiplatelet therapy: Aspirin 325 mg + Ticagrelor 180 mg load.\n'
    '3. Anticoagulation: Heparin bolus + infusion per protocol.\n'
    '4. High-intensity statin: Atorvastatin 80 mg daily.\n'
    '5. Beta-blocker: Metoprolol succinate 25 mg daily (hold if HR <60 or SBP <100).\n'
    '6. ACE inhibitor: Continue lisinopril, consider uptitration post-PCI.\n'
    '7. SGLT2 inhibitor: Consider empagliflozin post-stabilization for HFrEF + DM.\n'
    '8. Diuretic: IV furosemide 20 mg for volume overload.\n'
    '9. Glucose management: Insulin sliding scale, target 140-180.\n'
    '10. Admit to CICU for monitoring, serial troponins, echo in 24-48h.\n'
    '11. Cardiology consult (accepted). Nephrology consult for CKD dosing.\n'
    '12. Smoking cessation counseling (reinforce). Cardiac rehab referral post-discharge.'
)

# Save PDF
pdf.output('test_patient_james_anderson.pdf')
print("PDF created successfully: test_patient_james_anderson.pdf")