# Ecotech 12 Connect

The registration site is in `docs/`. GitHub Pages publishes `main` → `/docs` at:
https://shraycapital.github.io/ecotech12-association/

The fair copy says “10 October 2026 to Dussehra”. No venue is displayed.

## Email activation — complete before using the stall QR

Registrations use FormSubmit's native multipart form submission to `shray@urjatech.com`, including an optional PDF/DOC/DOCX attachment up to 5 MB. FormSubmit's default security challenge is retained. A successful frontend build does not verify inbox delivery.

1. Activate FormSubmit using the email it sends to `shray@urjatech.com` after the first submission. Check spam as well.
2. Submit a clearly marked candidate test from the live site, complete the security check and verify the email arrives with all selected fields and an optional sample attachment.
3. Repeat for a vendor in Hindi. The interface is translated; stable English field names and option values are used in the email for easy sorting.
4. Delete the test emails when finished. Do not print the QR for unattended registration until delivery is verified.

There is no candidate database or admin dashboard. The organiser's inbox is the intake record. Each submitted form includes a reference and timestamp. Restrict mailbox access and share details only with relevant members for the consented purpose. FormSubmit documents 30-day submission retention and does not retain file attachments in its archive.

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
