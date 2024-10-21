from openai import OpenAI
import subprocess
import os
import re
from fdfgen import forge_fdf

OPENAI_MODEL="gpt-3.5-turbo-0125"
# OPENAI_MODEL="gpt-4"
# OPENAI_MODEL="gpt-4-32k" # noaccess

key = os.environ.get("OPENAI_API_KEY")

filename_txt = os.sys.argv[1]

filename_pdf = os.sys.argv[2]

raw_form_fields = """
---
FieldType: Text
FieldName: F[0].P4[0].LastFirstMiddle[0]
FieldNameAlt: 1. A. VETERAN&apos;S NAME (Last, First, Middle Name).
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField2[0]
FieldNameAlt: 2. MOTHER&apos;S MAIDEN NAME.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].SSN[0]
FieldNameAlt: 6. SOCIAL SECURITY NUMBER. Enter 9 digit social security number.
FieldFlags: 0
FieldJustification: Left
FieldMaxLength: 9
---
FieldType: Text
FieldName: F[0].P4[0].DateTimeField4[0]
FieldNameAlt: 7. A. DATE OF BIRTH. Enter 2 digit month, 2 digit day, and 4 digit year.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField5[0]
FieldNameAlt: 7B. PLACE OF BIRTH (City and State). 
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField6[0]
FieldNameAlt: 10. A. MAILING ADDRESS (Street).
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField7[0]
FieldNameAlt: 10B. CITY.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField8[0]
FieldNameAlt: 10C. STATE.
FieldFlags: 0
FieldJustification: Center
FieldMaxLength: 2
---
FieldType: Text
FieldName: F[0].P4[0].TextField25[0]
FieldNameAlt: 10D. ZIP CODE.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField9[0]
FieldNameAlt: 10E. COUNTY.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField12[0]
FieldNameAlt: 16. WHICH V. A. MEDICAL CENTER OR  OUTPATIENT CLINIC DO YOU PREFER? (for listing of facilities visit www.va.gov/find-locations).
FieldFlags: 8392704
FieldJustification: Left
---
FieldType: Button
FieldName: F[0].P4[0].RadioButtonList[0]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: 2
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P4[0].RadioButtonList[1]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: 2
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P4[0].CheckBox7[0]
FieldNameAlt: 5. AMERICAN INDIAN OR ALASKA NATIVE.
FieldFlags: 0
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P4[0].CheckBox7[1]
FieldNameAlt: 5. WHAT IS YOUR RACE? (You may check more than one. Information is required for statistical purposes only.) ASIAN.
FieldFlags: 0
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P4[0].CheckBox7[2]
FieldNameAlt: 5. WHITE.
FieldFlags: 0
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P4[0].CheckBox7[3]
FieldNameAlt: 5. BLACK OR AFRICAN AMERICAN.
FieldFlags: 0
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P4[0].CheckBox7[4]
FieldNameAlt: 5. NATIVE HAWAIIAN OR OTHER PACIFIC  ISLANDER.
FieldFlags: 0
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P4[0].RadioButtonList[2]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: 2
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P4[0].RadioButtonList[3]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: 2
FieldStateOption: 3
FieldStateOption: 4
FieldStateOption: 5
FieldStateOption: Off
---
FieldType: Text
FieldName: F[0].P4[0].TextField2[1]
FieldNameAlt: 1B. PREFERRED NAME.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Button
FieldName: F[0].P4[0].RadioButtonList[4]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: 2
FieldStateOption: 3
FieldStateOption: 5
FieldStateOption: 4
FieldStateOption: 6
FieldStateOption: 7
FieldStateOption: Off
---
FieldType: Text
FieldName: F[0].P4[0].TextField5[1]
FieldNameAlt: 9. RELIGION.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField6[1]
FieldNameAlt: 11. A. HOME ADDRESS (Street).
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField7[1]
FieldNameAlt: 11B. CITY.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField8[1]
FieldNameAlt: 11C. STATE.
FieldFlags: 0
FieldJustification: Center
FieldMaxLength: 2
---
FieldType: Text
FieldName: F[0].P4[0].TextField25[1]
FieldNameAlt: 11D. ZIP CODE.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField9[1]
FieldNameAlt: 11E. COUNTY.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField10[0]
FieldNameAlt: 10F. HOME TELEPHONE NUMBER (optional) (Include area code).
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField11[0]
FieldNameAlt: 10G. MOBILE TELEPHONE NUMBER (optional) (Include area code).
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField23[0]
FieldNameAlt: 10H. E-MAIL ADDRESS (optional).
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField2[2]
FieldNameAlt: 13. A. NEXT OF KIN NAME.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField2[3]
FieldNameAlt: 13B. NEXT OF KIN ADDRESS.
FieldFlags: 8392704
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField2[4]
FieldNameAlt: 13C. NEXT OF KIN RELATIONSHIP.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField2[5]
FieldNameAlt: 13D. NEXT OF KIN TELEPHONE NUMBER
(Include Area Code).
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField2[6]
FieldNameAlt: 14B. EMERGENCY CONTACT TELEPHONE Number (Include Area Code). 
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField2[7]
FieldNameAlt: 15. DESIGNEE - INDIVIDUAL TO RECEIVE POSSESSION OF YOUR PERSONAL PROPERTY LEFT ON PREMISES UNDER V. A. CONTROL AFTER YOUR DEPARTURE OR AT THE TIME OF DEATH.  (Note: This does not constitute a will or transfer of title).
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Button
FieldName: F[0].P4[0].CheckBox7[5]
FieldNameAlt: 5. CHOOSE NOT TO ANSWER. 
FieldFlags: 0
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P4[0].CheckBox7[6]
FieldNameAlt: SECTION 1. GENERAL INFORMATION. Read information above. TYPE OF BENEFIT(S) APPLYING FOR: ENROLLMENT - V. A. Medical Benefits Package (Veteran meets and agrees to the enrollment eligibility criteria specified at 38 C F R 17.36).
FieldFlags: 0
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P4[0].CheckBox7[7]
FieldNameAlt: TYPE OF BENEFIT(S) APPLYING FOR: REGISTRATION (Complete Sections 1, 2, and 3) - V. A. Health Services (Veterans meets the &quot;Enrollment not required&quot; eligibility criteria specified at 38 C F R 17.37).
FieldFlags: 0
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: Off
---
FieldType: Text
FieldName: F[0].P4[0].TextField5[2]
FieldNameAlt: 8. PREFERRED LANGUAGE.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P4[0].TextField1[0]
FieldNameAlt: 14. A. EMERGENCY CONTACT NAME.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].LastFirstMiddle[0]
FieldNameAlt: VETERAN&apos;S NAME (Last, First, Middle). This field is a read only field and pre-populates from page 1.
FieldFlags: 8388609
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].SSN[0]
FieldNameAlt: SOCIAL SECURITY NUMBER. This field is a read only field and pre-populates from page 1.
FieldFlags: 8388609
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].TextField20[0]
FieldNameAlt: SECTION 4. DEPENDENT INFORMATION (Use a separate sheet for additional dependents). 1. SPOUSE&apos;S NAME (Last, First, Middle Name).
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].TextField20[1]
FieldNameAlt: 2. CHILD&apos;S NAME (Last, First, Middle Name).
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].TextField20[2]
FieldNameAlt: 1. A. SPOUSE&apos;S SOCIAL SECURITY NUMBER.
FieldFlags: 0
FieldJustification: Left
FieldMaxLength: 9
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[0]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: 2
FieldStateOption: Off
---
FieldType: Text
FieldName: F[0].P5[0].DateTimeField6[0]
FieldNameAlt: 1B. SPOUSE&apos;S DATE OF BIRTH. Enter 2 digit month, 2 digit day, and 4 digit year.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].DateTimeField5[0]
FieldNameAlt: 1D. DATE OF MARRIAGE. Enter 2 digit month, 2 digit day, and 4 digit year.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].TextField20[3]
FieldNameAlt: 1E. SPOUSE&apos;S ADDRESS AND TELEPHONE NUMBER (Street, City, State, ZIP - if different from Veteran&apos;s).
FieldFlags: 8392704
FieldJustification: Left
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[1]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: 2
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[2]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: 2
FieldStateOption: Off
---
FieldType: Text
FieldName: F[0].P5[0].TextField22[0]
FieldNameAlt: 2G. EXPENSES PAID BY YOUR DEPENDENT CHILD FOR COLLEGE, VOCATIONAL REHABILITATION OR TRAINING (e.g., tuition, books, materials).
FieldFlags: 8392704
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].TextField20[4]
FieldNameAlt: 2B. CHILD&apos;S SOCIAL SECURITY NUMBER.
FieldFlags: 0
FieldJustification: Left
FieldMaxLength: 9
---
FieldType: Text
FieldName: F[0].P5[0].DateTimeField7[0]
FieldNameAlt: 2C. DATE CHILD BECAME YOUR DEPENDENT. Enter 2 digit month, 2 digit day, and 4 digit year.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[3]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: 2
FieldStateOption: 3
FieldStateOption: 4
FieldStateOption: Off
---
FieldType: Text
FieldName: F[0].P5[0].DateTimeField3[0]
FieldNameAlt: 2. A. CHILD&apos;S DATE OF BIRTH. Enter 2 digit month, 2 digit day, and 4 digit year.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].TextField17[0]
FieldNameAlt: SECTION 3. INSURANCE INFORMATION (Use a separate sheet for additional information). 1. ENTER YOUR HEALTH INSURANCE COMPANY NAME, ADDRESS AND TELEPHONE NUMBER (include coverage through spouse or other person).
FieldFlags: 8392704
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].TextField18[0]
FieldNameAlt: 2. NAME OF POLICY HOLDER.
FieldFlags: 8392704
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].TextField19[0]
FieldNameAlt: 3. POLICY NUMBER.
FieldFlags: 8392704
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].TextField19[1]
FieldNameAlt: 4. GROUP CODE.
FieldFlags: 8392704
FieldJustification: Left
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[4]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: 2
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[5]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: 2
FieldStateOption: Off
---
FieldType: Text
FieldName: F[0].P5[0].DateTimeField1[0]
FieldNameAlt: 6B. EFFECTIVE DATE. Enter 2 digit month, 2 digit day, and 4 digit year.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].TextField13[0]
FieldNameAlt: SECTION 2. MILITARY SERVICE INFORMATION. 1. A. LAST BRANCH OF SERVICE.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].DateTimeField8[0]
FieldNameAlt: 1B. LAST ENTRY DATE. Enter 2 digit month, 2 digit day, and 4 digit year.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].DateTimeField9[0]
FieldNameAlt: 1D. LAST DISCHARGE DATE. Enter 2 digit month, 2 digit day, and 4 digit year.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].TextField24[0]
FieldNameAlt: 1E. DISCHARGE TYPE.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].DateTimeField8[1]
FieldNameAlt: 1C. FUTURE DISCHARGE DATE. Enter 2 digit month, 2 digit day, and 4 digit year.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].TextField24[1]
FieldNameAlt: 1F. MILITARY SERVICE NUMBER.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[6]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: YES
FieldStateOption: NO
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[7]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: YES
FieldStateOption: NO
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[8]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: YES
FieldStateOption: NO
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[9]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: YES
FieldStateOption: NO
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[10]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: YES
FieldStateOption: NO
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[11]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: YES
FieldStateOption: NO
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[12]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: YES
FieldStateOption: NO
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[13]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: YES
FieldStateOption: NO
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[14]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: YES
FieldStateOption: NO
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[15]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: YES
FieldStateOption: NO
FieldStateOption: Off
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[16]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: 1
FieldStateOption: 2
FieldStateOption: 3
FieldStateOption: 5
FieldStateOption: 4
FieldStateOption: 6
FieldStateOption: 7
FieldStateOption: Off
---
FieldType: Text
FieldName: F[0].P5[0].MedicareClaimNumber[0]
FieldNameAlt: 6C. MEDICARE NUMBER.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Button
FieldName: F[0].P5[0].RadioButtonList[17]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: RETIRED
FieldStateOption: FULL TIME
FieldStateOption: PART TIME
FieldStateOption: NOT EMPLOYED
FieldStateOption: Off
---
FieldType: Text
FieldName: F[0].P5[0].TextField20[5]
FieldNameAlt: 1C. COMPANY NAME. (Complete if employed or retired).
FieldFlags: 8392704
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].TextField20[6]
FieldNameAlt: 1D. COMPANY ADDRESS (Complete if employed or retired - Street, City, State, ZIP ).
FieldFlags: 8392704
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].TextField20[7]
FieldNameAlt: 1E. COMPANY PHONE NUMBER  (Complete if employed or retired). (Include area code).
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P5[0].Date[0]
FieldNameAlt: 1B. DATE OF RETIREMENT. Enter 2 digit month, 2 digit day and 4 digit year.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P6[0].DateTimeField2[0]
FieldNameAlt: DATE OF SIGNATURE. Enter 2 digit month, 2 digit day and 4 digit year.
FieldFlags: 8388608
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P6[0].LastFirstMiddle[0]
FieldNameAlt: VETERAN&apos;S NAME (Last, First, Middle). This field is a read only field and pre-populates from page 1.
FieldFlags: 8388609
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P6[0].SSN[0]
FieldNameAlt: SOCIAL SECURITY NUMBER. This field is a read only field and pre-populates from page 1.
FieldFlags: 8388609
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P6[0].TextField21[0]
FieldNameAlt: See Section 8 and Assignment of Benefits above. SIGNATURE OF APPLICANT. (Sign in ink). This signature field can not be signed with a digital signature and the signee&apos;s name can not be typewritten into this space. This is a protected field. Please print the document and sign in ink.
FieldFlags: 8388609
FieldJustification: Left
---
FieldType: Text
FieldName: F[0].P6[0].NumericField2[0]
FieldNameAlt: SECTION 7. PREVIOUS CALENDAR YEAR GROSS ANNUAL INCOME OF VETERAN, SPOUSE AND DEPENDENT CHILDREN
(Use a separate sheet for additional dependents). 1. GROSS ANNUAL INCOME FROM EMPLOYMENT (wages, bonuses, tips, etc.) EXCLUDING INCOME FROM YOUR FARM, RANCH, PROPERTY OR BUSINESS. VETERAN. Enter Dollar Amount.
FieldFlags: 8388608
FieldJustification: Right
---
FieldType: Text
FieldName: F[0].P6[0].NumericField2[1]
FieldNameAlt: 1. SPOUSE. Enter Dollar Amount.
FieldFlags: 8388608
FieldJustification: Right
---
FieldType: Text
FieldName: F[0].P6[0].NumericField2[2]
FieldNameAlt: 1. CHILD 1. Enter Dollar Amount.
FieldFlags: 8388608
FieldJustification: Right
---
FieldType: Text
FieldName: F[0].P6[0].NumericField2[3]
FieldNameAlt: 2. NET INCOME FROM YOUR FARM, RANCH, PROPERTY OR BUSINESS. VETERAN. Enter Dollar Amount.
FieldFlags: 8388608
FieldJustification: Right
---
FieldType: Text
FieldName: F[0].P6[0].NumericField2[4]
FieldNameAlt: 2. SPOUSE. Enter Dollar Amount.
FieldFlags: 8388608
FieldJustification: Right
---
FieldType: Text
FieldName: F[0].P6[0].NumericField2[5]
FieldNameAlt: 2. CHILD 1. Enter Dollar Amount.
FieldFlags: 8388608
FieldJustification: Right
---
FieldType: Text
FieldName: F[0].P6[0].NumericField2[6]
FieldNameAlt: 3. LIST OTHER INCOME AMOUNTS (e.g., Social Security, compensation, pension, interest, dividends) EXCLUDING WELFARE. VETERAN. Enter Dollar Amount.
FieldFlags: 8388608
FieldJustification: Right
---
FieldType: Text
FieldName: F[0].P6[0].NumericField2[7]
FieldNameAlt: 3. SPOUSE. Enter Dollar Amount.
FieldFlags: 8388608
FieldJustification: Right
---
FieldType: Text
FieldName: F[0].P6[0].NumericField2[8]
FieldNameAlt: 3. CHILD 1. Enter Dollar Amount.
FieldFlags: 8388608
FieldJustification: Right
---
FieldType: Text
FieldName: F[0].P6[0].NumericField2[9]
FieldNameAlt: SECTION 8. PREVIOUS CALENDAR YEAR DEDUCTIBLE EXPENSES. 1. TOTAL NON-REIMBURSED MEDICAL EXPENSES PAID BY YOU OR YOUR SPOUSE (e.g., payments for doctors, dentists, medications, Medicare, health  insurance, hospital and nursing home) V. A. will calculate a deductible and the net medical expenses you may claim. Enter Dollar Amount.
FieldFlags: 8388608
FieldJustification: Right
---
FieldType: Text
FieldName: F[0].P6[0].NumericField2[10]
FieldNameAlt: 2. AMOUNT YOU PAID LAST CALENDAR YEAR FOR FUNERAL AND BURIAL EXPENSES (INCLUDING PREPAID BURIAL EXPENSES) FOR YOUR DECEASED SPOUSE OR DEPENDENT CHILD (Also enter spouse or child&apos;s information in Section 6.) Enter Dollar Amount.
FieldFlags: 8388608
FieldJustification: Right
---
FieldType: Text
FieldName: F[0].P6[0].NumericField2[11]
FieldNameAlt: 3. AMOUNT YOU PAID LAST CALENDAR YEAR FOR YOUR COLLEGE OR VOCATIONAL EDUCATIONAL EXPENSES (e.g., tuition, books, fees, materials) 
DO NOT LIST YOUR DEPENDENTS&apos; EDUCATIONAL EXPENSES. Enter Dollar Amount.
FieldFlags: 8388608
FieldJustification: Right
---
FieldType: Button
FieldName: F[0].P6[0].RadioButtonList[0]
FieldFlags: 49152
FieldJustification: Left
FieldStateOption: Yes, I will provide my household financial information for last calendar year. Complete applicable Sections VII and VIII. Sign and date the form in the Assignment of Benefits section.
FieldStateOption: No, I do not wish to provide financial information in Sections VII through VIII. If I am enrolled, I agree to pay applicable VA copayments. Sign and date the form in the Assignment of Benefits section.
FieldStateOption: Off

"""

def sanitize_text(text):

    client = OpenAI()

    completion = client.chat.completions.create(
      model=OPENAI_MODEL,
      messages=[
        {"role": "system", "content": """
        Please sanitize the text using these rules:
        - Format dates as MM/DD/YYYY
        - Format names as Last name, First name
        - Correct grammatical errors
        - Correct syntactical errors
        - Correct typos
        - Format amounts
        """},
        {"role": "user", "content": f"""
        Text:
        {text}
        """
        }
      ]
    )

    return completion.choices[0].message.content if len(completion.choices) > 0 else None


def fill_form_fields_using_openai(text):

    client = OpenAI()

    completion = client.chat.completions.create(
      model=OPENAI_MODEL,
      messages=[
        {"role": "system", "content": f"""

You are assisting the user to fill a form.

The form has these instructions

############### INSTRUCTIONS: START

INSTRUCTIONS FOR COMPLETING ENROLLMENT
APPLICATION FOR HEALTH BENEFITS
Please Read Before You Start . . . What is VA Form 10-10EZ used for?

For Veterans to apply for enrollment in the VA health care system. The information provided on this form will be used by VA to
determine your eligibility for medical benefits and on average will take 30 minutes to complete. This includes the time it will take to
read instructions, gather the necessary facts and fill out the form.

Where can I get help filling out the form and if I have questions?

You may use ANY of the following to request assistance:
• Ask VA to help you fill out the form by calling us at 1-877-222-VETS (8387).
• Go to www.va.gov/health-care for information about VA health benefits.
• Contact the Enrollment Coordinator at your local VA health care facility.
• Contact a National or State Veterans Service Organization.

Definitions of terms used on this form:

• SERVICE-CONNECTED (SC): A VA determination that an illness or injury was incurred or aggravated in the line of duty, in the
active military, naval or air service.
• COMPENSABLE: A VA determination that a service-connected disability is severe enough to warrant monetary compensation.
• NONCOMPENSABLE: A VA determination that a service-connected disability is not severe enough to warrant monetary
compensation.
• NONSERVICE-CONNECTED (NSC): A Veteran who does not have a VA determined service-related condition.

Getting Started:

ALL VETERANS MUST COMPLETE SECTIONS I - III.

Directions for Sections I - III:
Section I - General Information: Answer all questions.
Type of Benefit Applying For:
• Enrollment - Veterans applying for enrollment for the Full Medical Benefits Package provide in 38 C.F.R. 17.38 must meet the
eligibility requirements of 38 C.F.R. 17.36.
• Registration - For Registrations, only complete Sections I, II, and III. Enrollment not required - Veterans requesting an eligibility
assessment, clinical evaluation, care or treatment pursuant to a special treatment authority provided in 38 C.F.R. 17.37:
• Care for a Veteran with a VA service connected disability rating of 50% or greater
• Care for a VA rated service connected disability
• Care for psychosis or other mental illness
• Care for Military Sexual Trauma treatment (MST)
• Catastrophically Disabled Examination
• A veteran who was discharged or released from active military service for a disability incurred or aggravated in the line of duty can
receive VA care for the 12-month period following discharge or release
• Care for a Veteran participating in VA's vocational rehabilitation program under 38 U.S.C. 31
Section II - Military Service Information: If you are not currently receiving benefits from VA, you may attach a copy of your
discharge or separation papers from the military (such as DD-214 or, for WWII Veterans, a "WD" Form), with your signed
application to expedite processing of your application. If you are currently receiving benefits from VA, we will cross-reference
your information with VA data.
Section III - Insurance Information: Include information for all health insurance companies that cover you, this includes
coverage provided through a spouse or significant other. Bring your insurance cards, Medicare and/or Medicaid card with you to
each health care appointment.

VA FORM
APR 2023

10-10EZ

Complete only the sections that apply to you; sign and date the form.

HEC

PAGE 1 OF 6

Directions for Sections IV-IX:
Section IV - Dependent Information: Include the following:
• Your spouse even if you did not live together, as long as you contributed support last calendar year.
• Your biological children, adopted children, and stepchildren who are unmarried and under the age of 18, or at least 18 but under 23 and
attending high school, college or vocational school (full or part-time), or became permanently unable to support themselves before age 18.
• Child support contributions. Contributions can include tuition or clothing payments or payments of medical bills.
Section V - Employment Information:
• Veterans Employment Status
• Date of Retirement
• Company Name

• Company Address
• Company Phone Number

Section VI - Financial Disclosure: ONLY NSC AND 0% NONCOMPENSABLE SC VETERANS MUST COMPLETE
THIS SECTION TO DETERMINE ELIGIBILITY FOR VA HEALTH CARE ENROLLMENT AND/OR CARE OR
SERVICES.
Financial Disclosure Requirements Do Not Apply To:
• a former Prisoner of War; or
• those in receipt of a Purple Heart; or
• a recently discharged Combat Veteran; or
• those discharged for a disability incurred or aggravated in the line of duty; or
• those receiving VA SC disability compensation; or
• those receiving VA pension; or
• those in receipt of Medicaid benefits; or
• those who served in an Agent Orange exposure location; or
• those who served in SW Asia during the Gulf War between August 2, 1990 and November 11, 1998; or
• those who served at least 30 days at Camp Lejeune between August 1, 1953 and December 31, 1987.
You are not required to disclose your financial information; however, VA is not currently enrolling new applicants who decline to
provide their financial information unless they have other qualifying eligibility factors. If a financial assessment is not used to
determine your priority for enrollment you may choose not to disclose your information. However, if a financial assessment is used
to determine your eligibility for cost-free medication, travel assistance or waiver of the travel deductible, and you do not disclose
your financial information, you will not be eligible for these benefits.
Section VII - Previous Calendar Year Gross Annual Income of Veteran, Spouse and Dependent Children
Report:
• Gross annual income from employment, except for income from your farm, ranch, property or business. Include your wages, bonuses,
tips, severance pay and other accrued benefits and your child's income information if it could have been used to pay your household
expenses.
• Net income from your farm, ranch, property, or business.
• Other income amounts, including retirement and pension income, Social Security Retirement and Social Security Disability income,
compensation benefits such as VA disability, unemployment, Workers and black lung, cash gifts, interest and dividends, including tax
exempt earnings and distributions from Individual Retirement Accounts (IRAs) or annuities.
Do Not Report:
Donations from public or private relief, welfare or charitable organizations; Supplemental Security Income (SSI) and need-based payments
from a government agency; profit from the occasional sale of property; income tax refunds, reinvested interest on Individual Retirement
Accounts (IRAs); scholarships and grants for school attendance; disaster relief payments; reimbursement for casualty loss; loans; Radiation
Compensation Exposure Act payments; Agent Orange settlement payments; Alaska Native Claims Settlement Acts Income, payments to
foster parent; amounts in joint accounts in banks and similar institutions acquired by reason of death of the other joint owner; Japanese
ancestry restitution under Public Law 100-383; cash surrender value of life insurance; lump-sum proceeds of life insurance policy on a
Veteran; and payments received under the Medicare transitional assistance program.
Section VIII - Previous Calendar Year Deductible Expenses
Report non-reimbursed medical expenses paid by you or your spouse. Include expenses for medical and dental care, drugs, eyeglasses,
Medicare, medical insurance premiums and other health care expenses paid by you for dependents and persons for whom you have a legal
or moral obligation to support. Do not list expenses if you expect to receive reimbursement from insurance or other sources. Report last
illness and burial expenses, e.g., prepaid burial, paid by the Veteran for spouse or dependent(s).
Section IX - Consent to Copays and to Receive Communications
By submitting this application, you are agreeing to pay the applicable VA copayments for care or services (including urgent care) as
required by law. You also agree to receive communications from VA to your supplied email, home phone number, or mobile
number. However, providing your email, home phone number, or mobile number is voluntary.
VA FORM 10-10EZ, APR 2023

HEC

PAGE 2 OF 6

Submitting Your Application

1. You or an individual to whom you have delegated your Power of Attorney must sign and date the form. If you sign with an "X", 2
people you know must witness you as you sign. They must sign the form and print their names. If the form is not signed and dated
appropriately, VA will return it for you to complete.
2. Attach any continuation sheets, a copy of supporting materials and your Power of Attorney documents to your application.
Where do I send my application?
Mail the original application and supporting materials to the Health Eligibility Center, 2957 Clairmont Road, Suite 200, Atlanta, GA 30329.
PAPERWORK REDUCTION ACT AND PRIVACY ACT INFORMATION

The Paperwork Reduction Act of 1995 requires us to notify you that this information collection is in accordance with the clearance requirements of Section
3507 of the Paperwork Reduction Act of 1995. We may not conduct or sponsor, and you are not required to respond to, a collection of information unless it
displays a valid OMB number. We anticipate that the time expended by all individuals who must complete this form will average 30 minutes. This includes the
time it will take to read instructions, gather the necessary facts and fill out the form.
Privacy Act Information: VA is asking you to provide the information on this form under 38 U.S.C. Sections 1705,1710, 1712, and 1722 in order for VA to
determine your eligibility for medical benefits. Information you supply may be verified from initial submission forward through a computer-matching program.
VA may disclose the information that you put on the form as permitted by law. VA may make a "routine use" disclosure of the information as outlined in the
Privacy Act systems of records notices and in accordance with the VHA Notice of Privacy Practices. Providing the requested information is voluntary, but if any
or all of the requested information is not provided, it may delay or result in denial of your request for health care benefits. Failure to furnish the information will
not have any effect on any other benefits to which you may be entitled. If you provide VA your Social Security Number, VA will use it to administer your VA
benefits. VA may also use this information to identify Veterans and persons claiming or receiving VA benefits and their records, and for other purposes
authorized or required by law.


############### INSTRUCTIONS: END




The form has multiple fields defined next. 

This is the form definition...

{raw_form_fields}

Instructions for openai assistant:
- Each field lives between --- blocks of characters
- Analyse the input text and then find the best response to each field
- If you don't find a valid response just return empty string instead of "Data not provided" or similar
- Use the FieldNameAlt attribute to get the answer provided in the Answers provided by the user.
- When you are asked to print output, use FieldName attribute instead of the FieldNameAlt attribute
- The FieldType indicates if the field is Text, Button or other types.

IMPORTANT: FieldName attribute must be printed and FieldNameAlt is ignored when you output your response.

Response must be formatted in CSV format using FieldName and the best value you found.

FieldName,Response

"""},
        {"role": "user", "content": f"""
Text:

{text}
    """}
      ]
    )

    return completion.choices[0].message.content if len(completion.choices) > 0 else None


def load_text_from_file(filename_txt):

    text = f"""
    I am Nathan Jones, but I prefer to be called Nate. I am applying for VA health care enrollment as of January 12, 2024. I was born on January 3, 1975, in Lake Russell, MT, and identify as a man with American Indian or Alaska Native ancestry. My mother's maiden name is Roman. I speak English and practice Christianity.
    I currently reside at 71121 Morgan Cape Suite 303, North, WY, 60565, in South Ryanstad. My email address is Nathan-744@example.com. I am separated from my wife, Veronica Wright, who now resides at 662 Houston Highway, Ronaldstad, LA 86922. We have two daughters, Sara Jones, born on August 31, 2021, and Laura Michelle Jones, born on October 31, 2022.
    My sibling, Roger Carter, is my next of kin and can be reached aboard the USS Walton at FPO AP 21321, with a contact number of (555)999-3183. Lauren Davis is my emergency contact, available at (555)614-7286.
    I served in the Air Force from January 26, 2003, to March 25, 2005, and was honorably discharged. My military service number is 54899929. I have served during the Gulf War.
    My health insurance provider is Smith, Riley and Diaz, with an office located at Unit 6624 Box 5301, DPO AP 14795, and a contact number of (555)955-2427. The policy is under my name, Nathan Jones, with the policy number 193-860-9100 and group code 86-8561. I have not enrolled in Medicaid or Medicare Part A as of April 17, 2021.
    Currently, I am employed part-time and plan to retire on September 18, 2026, from Lopez-Mooney, located at 014 Alexis Village Suite 328, Port Stevenborough, IA 87238. The contact number for my workplace is (555)406-2272. My financial disclosure includes an annual income of $35,017.
    My preferred VA facility for health care services is the Cheyenne VA Medical Center.
    """

    with open(filename_txt) as f:
        text = f.read()
        
    return text

         
def translate_string_to_tuples(input_string):
    
    l = []
    
    for s in input_string.split('\n'):
        fv = s.replace('"','').replace('Field: ','').split(',')
        if len(fv) >= 2:
            value = ','.join(fv[1:])
            value = value.strip()
            l.append((fv[0], value))

    return l

text = load_text_from_file(filename_txt)

'''
response = """
F[0].P4[0].LastFirstMiddle[0],Nathan Jones
F[0].P4[0].TextField2[1],Nate
F[0].P4[0].DateTimeField4[0],01/03/1975
F[0].P4[0].TextField5[0],Lake Russell, MT
F[0].P4[0].RadioButtonList[0],1
F[0].P4[0].CheckBox7[0],1
F[0].P4[0].TextField2[0],Roman
F[0].P4[0].TextField5[1],Christianity
F[0].P4[0].TextField6[0],71121 Morgan Cape Suite 303
F[0].P4[0].TextField7[0],North
F[0].P4[0].TextField8[0],WY
F[0].P4[0].TextField25[0],60565
F[0].P4[0].TextField23[0],Nathan-744@example.com
F[0].P4[0].TextField2[2],Roger Carter
F[0].P4[0].TextField2[3],FPO AP 21321
F[0].P4[0].TextField2[4],Sibling
F[0].P4[0].TextField2[5],(555)999-3183
F[0].P4[0].TextField1[0],Lauren Davis
F[0].P4[0].TextField2[6],(555)614-7286
F[0].P4[0].RadioButtonList[4],2
F[0].P5[0].TextField20[0],Veronica Wright
F[0].P5[0].TextField20[1],Sara Jones,Laura Michelle Jones
F[0].P5[0].TextField20[3],662 Houston Highway, Ronaldstad, LA 86922
F[0].P5[0].TextField20[5],Nathan Jones
F[0].P5[0].TextField17[0],Smith, Riley and Diaz, Unit 6624 Box 5301, DPO AP 14795,(555)955-2427
F[0].P5[0].TextField18[0],Nathan Jones
F[0].P5[0].TextField19[0],193-860-9100
F[0].P5[0].TextField19[1],86-8561
F[0].P5[0].TextField13[0],Air Force
F[0].P5[0].DateTimeField8[0],01/26/2003
F[0].P5[0].DateTimeField9[0],03/25/2005
F[0].P5[0].TextField24[0],Honorable
F[0].P5[0].TextField24[1],54899929
F[0].P5[0].RadioButtonList[0],1
F[0].P5[0].TextField20[5],54899929
F[0].P5[0].TextField20[6],014 Alexis Village Suite 328, Port Stevenborough, IA 87238
F[0].P5[0].TextField20[7],(555)406-2272
F[0].P5[0].Date[0],09/18/2026
F[0].P5[0].DateTimeField1[0],08/31/2021,10/31/2022
F[0].P5[0].RadioButtonList[17],2
F[0].P6[0].TextField1[0],Cheyenne VA Medical Center
F[0].P6[0].NumericField2[0],35017
F[0].P6[0].RadioButtonList[0],Yes, I will provide my household financial information for last calendar year. Complete applicable Sections VII and VIII. Sign and date the form in the Assignment of Benefits section."""
'''

'''
response = """
FieldName,Value
1. A. VETERAN&apos;S NAME (Last, First, Middle Name),Cuevas, Gabriel Anthony
2. MOTHER&apos;S MAIDEN NAME,N/A
6. SOCIAL SECURITY NUMBER. Enter 9 digit social security number.,
7. A. DATE OF BIRTH. Enter 2 digit month, 2 digit day, and 4 digit year,09/13/1975
7B. PLACE OF BIRTH (City and State),South Michael, TX
10. A. MAILING ADDRESS (Street),6592 Alison Plaza
10B. CITY,West
10C. STATE,NM
10D. ZIP CODE,51554
10E. COUNTY,Thomasland
10F. HOME TELEPHONE NUMBER (optional) (Include area code),(555)679-4481
10G. MOBILE TELEPHONE NUMBER (optional) (Include area code),N/A
10H. E-MAIL ADDRESS (optional),Gabriel-716@example.com
13. A. NEXT OF KIN NAME,Sara Green
13B. NEXT OF KIN ADDRESS,77890 Carter Underpass, Wagnermouth, VI 03787
13C. NEXT OF KIN RELATIONSHIP,N/A
13D. NEXT OF KIN TELEPHONE NUMBER(Include Area Code),(555)414-5028
14B. EMERGENCY CONTACT TELEPHONE Number (Include Area Code). ,Judy Dillon (555)875-3142
15. DESIGNEE - INDIVIDUAL TO RECEIVE POSSESSION OF YOUR PERSONAL PROPERTY LEFT ON PREMISES UNDER V. A. CONTROL AFTER YOUR DEPARTURE OR AT THE TIME OF DEATH.  (Note: This does not constitute a will or transfer of title).,N/A
5. AMERICAN INDIAN OR ALASKA NATIVE,Off
5. WHAT IS YOUR RACE? (You may check more than one. Information is required for statistical purposes only.) ASIAN,Off
5. WHITE,1
5. BLACK OR AFRICAN AMERICAN,Off
5. NATIVE HAWAIIAN OR OTHER PACIFIC  ISLANDER,Off
8. PREFERRED LANGUAGE,Polish
9. RELIGION,Christianity
11. A. HOME ADDRESS (Street),6592 Alison Plaza
11B. CITY,West
11C. STATE,NM
11D. ZIP CODE,51554
11E. COUNTY,Thomasland
1. SPOUSE&apos;S NAME (Last, First, Middle Name),Turner, Diana Christina
2. CHILD&apos;S NAME (Last, First, Middle Name),Cuevas, Sara Terry
1. A. SPOUSE&apos;S SOCIAL SECURITY NUMBER.,N/A
1B. SPOUSE&apos;S DATE OF BIRTH. Enter 2 digit month, 2 digit day, and 4 digit year.,N/A
1D. DATE OF MARRIAGE. Enter 2 digit month, 2 digit day, and 4 digit year.,N/A
1E. SPOUSE&apos;S ADDRESS AND TELEPHONE NUMBER (Street, City, State, ZIP - if different from Veteran&apos;s),7777 Hickman Flat Apt. 640, Haynesburgh, UT 50528
2. NAME OF POLICY HOLDER.,Jones, Martinez and Hart
3. POLICY NUMBER.,352-422-5211
4. GROUP CODE.,00-2513
6C. MEDICARE NUMBER.,N/A
1C. COMPANY NAME. (Complete if employed or retired). ,N/A
1D. COMPANY ADDRESS (Complete if employed or retired - Street, City, State, ZIP ).,N/A
1E. COMPANY PHONE NUMBER  (Complete if employed or retired). (Include area code),N/A
1B. DATE OF RETIREMENT. Enter 2 digit month, 2 digit day and 4 digit year.,N/A
DATE OF SIGNATURE. Enter 2 digit month, 2 digit day and 4 digit year.,01/12/2024
1. GROSS ANNUAL INCOME FROM EMPLOYMENT (wages, bonuses, tips, etc.) EXCLUDING INCOME FROM YOUR FARM, RANCH, PROPERTY OR BUSINESS. VETERAN. Enter Dollar Amount.,30360
1. SPOUSE. Enter Dollar Amount.,N/A
1. CHILD 1. Enter Dollar Amount.,N/A
2. NET INCOME FROM YOUR FARM, RANCH, PROPERTY OR BUSINESS. VETERAN. Enter Dollar Amount.,N/A
2. SPOUSE. Enter Dollar Amount.,N/A
2. CHILD 1. Enter Dollar Amount.,N/A
3. LIST OTHER INCOME AMOUNTS (e.g., Social Security, compensation, pension, interest, dividends) EXCLUDING WELFARE. VETERAN. Enter Dollar Amount.,740
3. SPOUSE. Enter Dollar Amount.,N/A
3. CHILD 1. Enter Dollar Amount.,N/A
1. TOTAL NON-REIMBURSED MEDICAL EXPENSES PAID BY YOU OR YOUR SPOUSE (e.g., payments for doctors, dentists, medications, Medicare, health  insurance, hospital and nursing home) V. A. will calculate a deductible and the net medical expenses you may claim. Enter Dollar Amount.,37330
2. AMOUNT YOU PAID LAST CALENDAR YEAR FOR FUNERAL AND BURIAL EXPENSES (INCLUDING PREPAID BURIAL EXPENSES) FOR YOUR DECEASED SPOUSE OR DEPENDENT CHILD (Also enter spouse or child&apos;s information in Section 6.) Enter Dollar Amount.,N/A
3. AMOUNT YOU PAID LAST CALENDAR YEAR FOR YOUR COLLEGE OR VOCATIONAL EDUCATIONAL EXPENSES (e.g., tuition, books, fees, materials).,N/A
Yes, I will provide my household financial information for last calendar year. Complete applicable Sections VII and VIII. Sign and date the form in the Assignment of Benefits section.,Off"""
'''

sanitized_text = sanitize_text(text)
print('-'*40)
print('sanitized_text')
print(sanitized_text)

response = fill_form_fields_using_openai(sanitized_text)

print('-'*40)
print('response...')
print(response)

'''
# format field dict
form_fields_dict = {}
key = None
value = None
for idx, line in enumerate(raw_form_fields.split('\n')):
    if line.count('FieldName:'):
        key = line.split(': ')[1]
    if line.count('FieldNameAlt:'):
        value = line.split(': ')[1]
    if key and value:
        form_fields_dict[value] = key
        key = None
        value = None

print('-'*40)
for key in form_fields_dict.keys():
    value = form_fields_dict[key]
    print(f'   key "{key}"  value: "{value}"')

print('-'*40)
response_lines = []
found = 0
for idx, response_line in enumerate(response.split('\n')):
    if idx < 2: continue
    for key in form_fields_dict.keys():
        value = form_fields_dict[key]
        if key in response_line:
            print('   response_line:', response_line)
            response_line_new = response_line.replace(key,value)
            print('   response_line_new:', response_line_new)
            response_lines.append(response_line_new)
            found += 1
            break

if found:
    print('   found lines with inverted field name:', found)
    response = '\n'.join(response_lines)
'''

# Cleaning data
response = response.replace('Data not provided', '')
response = response.replace('DATA NOT PROVIDED', '')
response = response.replace('Not provided', '')

# Call the function to translate the string into a list of tuples
fields = translate_string_to_tuples(response)
for f in fields:
    print(f)

fdf = forge_fdf("",fields,[],[],[])

with open("my-new-data.fdf", "wb") as fdf_file:
    fdf_file.write(fdf)

pdftk_cmd = "pdftk /data/va_form_10-10ez.pdf fill_form my-new-data.fdf output " + filename_pdf
subprocess.run(pdftk_cmd.split())
# pdftk /data/va_form_10-10ez.pdf fill_form my-new-data.fdf output my-filled-form.pdf
