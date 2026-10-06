# Ecotech 12 Connect

The registration site is in `docs/`. GitHub Pages publishes `main` → `/docs` at:
https://shraycapital.github.io/ecotech12-association/

The fair copy says “10 October 2026 to Dussehra”. No venue is displayed.

## Email delivery

Activated and verified on 6 October 2026: FormSubmit accepted the post-activation test and the organiser confirmed receipt at the original organiser inbox. Browser tests also verified candidate and vendor flows, Hindi switching, required inputs, consent and a complete local multipart submission with an attachment. Native production CAPTCHA and attachment inbox delivery should be included in the stall team's final phone test.

Print assets: [A4 poster](docs/stall-poster.pdf) and [QR image](docs/registration-qr.png). The QR was independently decoded from the image and rendered PDF and resolves to the live HTTPS site.

### Activation / re-testing steps for future changes

Registrations use FormSubmit's activated native multipart submission endpoint, with a copy to `ecotech12ia@gmail.com`, including an optional PDF/DOC/DOCX attachment up to 5 MB. The original organiser inbox remains the primary delivery destination. Public contact links and the poster use only `ecotech12ia@gmail.com`. FormSubmit's default security challenge is retained. A successful frontend build does not verify inbox delivery.

1. Activate FormSubmit using the email it sends to the original organiser inbox after the first submission. Check spam as well.
2. Submit a clearly marked candidate test from the live site, complete the security check and verify the email arrives with all selected fields and an optional sample attachment.
3. Repeat for a vendor in Hindi. The interface is translated; stable English field names and option values are used in the email for easy sorting.
4. Delete the test emails when finished. Do not print the QR for unattended registration until delivery is verified.

Registrations are also delivered by FormSubmit webhook to an organiser-owned, private Google Sheet with Candidates and Vendors tabs. The Google Apps Script endpoint appends validated submissions, deduplicates references and never returns registration records. Keep Sheet sharing restricted. The public webhook URL is not an authentication secret; it allows submission but not reading existing data.

Open the private Sheet in the organiser's Google account, then choose **File → Download → Microsoft Excel (.xlsx)** to export both tabs. CVs and brochures remain in the email inbox; the Sheet records the attachment filename. Each registration includes a reference and timestamp for matching the email. Historical emails are not automatically imported. FormSubmit documents 30-day submission retention and does not retain file attachments in its archive.

The webhook is configured by the `_webhook` hidden field in `docs/index.html`. Update the existing Apps Script deployment to preserve that URL. Restrict mailbox and Sheet access, and share details only with relevant members for the consented purpose. If a webhook delivery fails, the email remains the fallback intake record.

### Apps Script maintenance

`integrations/registration-intake.gs` contains the handler template. When installing this template, set the Apps Script property `REGISTRATION_SHEET_ID` to the private workbook ID before deployment; the existing deployment already has its destination configured. Native FormSubmit submissions replace spaces in field names with underscores, and the webhook can JSON-encode `form_data` as a string. The handler accepts both native and AJAX formats. Keep the direct HtmlService acknowledgement: the ContentService redirect caused the native FormSubmit flow to show a server error after writing a row.

Verified on 6 October 2026 with a live browser candidate submission, CAPTCHA, matching Sheet reference and successful return to `thanks.html`. The previously missed pre-integration registration was recovered from its original email with its original consent version and timestamp preserved.

## Editing

- `docs/index.html`: English landing-page copy, event details, email recipient.
- `docs/data.js`: bilingual industry and service options and landing-page translations.
- `docs/app.js`: form fields, translations, step validation and email payload.
- `docs/style.css`: responsive styling.
- `docs/thanks.html`: bilingual return page after the processor's confirmation.

Update the email consistently in all files if changing the organiser. A different recipient needs its own activation. No API key or secret belongs in this static repository.

## Research

The association membership roster was reviewed on 6 October 2026 alongside 18 public company references. 126 roster entries were retained in the separate research report, including unnamed plots and cancelled entries. Membership, occupancy, company activity and current vacancies are separate facts. Name-inferred sector classifications need confirmation with members. Website role and vendor categories are a routing taxonomy, not claims of open vacancies or purchasing requirements.

## LinkedIn

An optional LinkedIn profile link is included. Full automatic profile import is not enabled. Standard LinkedIn OpenID Connect provides name/photo and optionally email, not a full employment or skills history. Adding optional sign-in requires an approved LinkedIn developer app and a secure OAuth callback backend. Never put a client secret in the frontend or scrape candidate profiles.

## Validation

Test required inputs, invalid phone/email/PIN/profile URLs, optional skipping, industry-specific roles, language switching without losing answers, independent candidate/vendor values, Back navigation, consent, attachment size/type and a live inbox delivery test. No personal data is written to browser local storage or repository files by the site.

References: https://formsubmit.co/documentation · https://formsubmit.co/help · https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin-v2
