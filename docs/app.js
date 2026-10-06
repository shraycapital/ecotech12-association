'use strict';
(() => {
 const $=s=>document.querySelector(s), form=$('#registration-form');
 let lang='en',kind='candidate',step=0;
 const values={candidate:{},vendor:{}},files={candidate:null,vendor:null},labels={};
 const t=(en,hi)=>lang==='hi'?hi:en;
 const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const tr=pair=>pair[lang==='hi'?1:0];
 const steps=()=>[t('Your details','आपकी जानकारी'),kind==='candidate'?t('Your interests','आपकी रुचि'):t('Your services','आपकी सेवाएँ'),t('A little more','थोड़ी और जानकारी'),t('Review & submit','जाँचें और जमा करें')];
 const key=id=>id.replaceAll('_',' ');
 function field(id,en,hi,type='text',required=false,opts={}){
  labels[id]=[en,hi];(opts.options||[]).forEach(p=>translations.set(...p));const v=values[kind][id]??'';const attrs=`id="${id}" name="${key(id)}" ${required?'required':''} ${opts.autocomplete?`autocomplete="${opts.autocomplete}"`:''}`;
  let control=type==='select'?`<select ${attrs}><option value="">${t('Select an option','विकल्प चुनें')}</option>${opts.options.map(o=>`<option value="${esc(o[0])}" ${o[0]===v?'selected':''}>${esc(tr(o))}</option>`).join('')}</select>`:type==='textarea'?`<textarea ${attrs} maxlength="1500" placeholder="${esc(opts.placeholder||'')}">${esc(v)}</textarea>`:type==='file'?`<input ${attrs} type="file" accept=".pdf,.doc,.docx" ${files[kind]?'data-preserved="true"':''}>`:`<input ${attrs} type="${type}" value="${esc(v)}" ${type==='number'?'min="0" max="10000000" step="1"':'maxlength="250"'} ${opts.pattern?`pattern="${opts.pattern}"`:''} ${opts.inputmode?`inputmode="${opts.inputmode}"`:''} placeholder="${esc(opts.placeholder||'')}">`;
  return `<div class="field ${opts.full?'full':''}"><label for="${id}">${esc(t(en,hi))} ${required?'*':`<span class="optional">${t('(optional)','(वैकल्पिक)')}</span>`}</label>${control}${opts.hint?`<p class="hint" id="${id}-hint">${esc(opts.hint)}</p>`:''}</div>`;
 }
 function checks(id,en,hi,options){labels[id]=[en,hi];options.forEach(p=>translations.set(...p));const selected=values[kind][id]||[];return `<fieldset class="field-group"><legend>${t(en,hi)} <span class="optional">${t('(choose any)','(एक या अधिक चुनें)')}</span></legend><div class="checks">${options.map((o,i)=>`<label class="check-chip"><input type="checkbox" name="${key(id)}" data-key="${id}" value="${esc(o[0])}" ${selected.includes(o[0])?'checked':''}>${esc(tr(o))}</label>`).join('')}</div></fieldset>`;}
 const title=(en,hi,descEn,descHi)=>`<h3 class="form-title" tabindex="-1">${t(en,hi)}</h3><p class="form-description">${t(descEn,descHi)}</p>`;
 const wrap=html=>`<div class="field-grid">${html}</div>`;
 function capture(){
  $('#fields').querySelectorAll('input,select,textarea').forEach(el=>{if(!el.name)return;if(el.type==='file'){if(el.files.length)files[kind]=el.files[0];return;}if(el.type==='checkbox'){if(el.dataset.key){values[kind][el.dataset.key]=[...$('#fields').querySelectorAll('input[data-key="'+el.dataset.key+'"]:checked')].map(x=>x.value);}else values[kind][el.id]=el.checked;}else values[kind][el.id]=el.value;});
 }
 function contact(){return title('Let’s get to know you.','आइए, आपसे परिचय करें।','We only need a few details to get started.','शुरुआत के लिए बस कुछ ज़रूरी जानकारी।')+wrap(
 field('Full_name','Full name','पूरा नाम','text',true,{autocomplete:'name'})+
 field('Mobile','Mobile number','मोबाइल नंबर','tel',true,{autocomplete:'tel',inputmode:'tel',placeholder:t('10-digit Indian mobile','10 अंकों का भारतीय मोबाइल'),hint:t('You can include +91.','आप +91 भी लिख सकते हैं।')})+
 field('email','Email address','ईमेल पता','email',false,{autocomplete:'email'})+
 field('Locality','Current city / locality','वर्तमान शहर / इलाका','text',true,{autocomplete:'address-level2',placeholder:t('e.g. Greater Noida West','जैसे ग्रेटर नोएडा वेस्ट')})+
 field('PIN_code','PIN code','पिन कोड','text',false,{inputmode:'numeric',pattern:'[1-9][0-9]{5}',autocomplete:'postal-code'})+
 field('Contact_preference','Preferred contact method','संपर्क का पसंदीदा माध्यम','select',false,{options:[['Phone call','फ़ोन कॉल'],['WhatsApp on this number','इसी नंबर पर WhatsApp'],['Email','ईमेल']]})+
 field('Preferred_language','Preferred conversation language','बातचीत की पसंदीदा भाषा','select',false,{options:[['Hindi','हिन्दी'],['English','अंग्रेज़ी'],['Hindi or English','हिन्दी या अंग्रेज़ी'],['Other','अन्य']]})+
 (kind==='vendor'?field('Business_name','Business / trading name','व्यवसाय / दुकान का नाम','text',false,{autocomplete:'organization',hint:t('Independent workers may leave this blank.','स्वतंत्र कामगार इसे खाली छोड़ सकते हैं।')}):''));}
 function interests(){if(kind==='vendor')return title('What can you offer?','आप क्या सेवा दे सकते हैं?','Help members understand your products or services.','सदस्यों को अपने उत्पाद या सेवाएँ समझाएँ।')+wrap(
 field('Service_category','Main service / supply category','मुख्य सेवा / सप्लाई श्रेणी','select',true,{options:E12.services,full:true})+
 field('Offering','Describe your services or products','अपनी सेवाएँ या उत्पाद बताएँ','textarea',true,{full:true,placeholder:t('What do you supply or do? Mention your specialisation.','आप क्या काम या सप्लाई करते हैं? अपनी विशेषज्ञता बताएँ।')})+
 field('Business_type','Type of provider','प्रदाता का प्रकार','select',false,{options:[['Individual / freelancer','स्वतंत्र कामगार / फ्रीलांसर'],['Contractor / service firm','ठेकेदार / सेवा कंपनी'],['Manufacturer','निर्माता'],['Dealer / distributor / trader','डीलर / वितरक / व्यापारी']]})+
 field('Service_area','Areas you can serve','आप कहाँ सेवाएँ दे सकते हैं','select',true,{options:[['Ecotech 12 / Greater Noida','ईकोटेक 12 / ग्रेटर नोएडा'],['Noida / Greater Noida / Ghaziabad','नोएडा / ग्रेटर नोएडा / गाज़ियाबाद'],['Delhi NCR','दिल्ली NCR'],['Across Uttar Pradesh','पूरे उत्तर प्रदेश में'],['Across India','पूरे भारत में'],['Other — describe below','अन्य — नीचे बताएँ']]})+
 field('Other_service_area','Other service area / additional services','अन्य सेवा क्षेत्र / अतिरिक्त सेवाएँ','text',false,{full:true}));
 const industry=values.candidate.Industry||'';
 return title('Find your kind of work.','अपनी पसंद का काम चुनें।','Choose your main interest. You can mention other interests below.','मुख्य रुचि चुनें। दूसरी रुचियाँ नीचे लिख सकते हैं।')+wrap(
 field('Industry','Preferred industry','पसंदीदा उद्योग','select',true,{options:E12.sectors,full:true})+
 `<div class="field full" id="role-options">${checks('Interested_roles','Roles you’re interested in','आपकी पसंद के काम',[...(E12.roles[industry]||[]),...E12.commonRoles])}</div>`+
 field('Experience','Total work experience','कुल कार्य अनुभव','select',true,{options:[['Fresher / no experience','नया उम्मीदवार / अनुभव नहीं'],['Less than 1 year','1 वर्ष से कम'],['1–3 years','1–3 वर्ष'],['3–5 years','3–5 वर्ष'],['5–10 years','5–10 वर्ष'],['10+ years','10 वर्ष से अधिक']]})+
 field('Education','Highest education','सबसे अधिक शिक्षा','select',true,{options:[['No formal schooling','औपचारिक शिक्षा नहीं'],['Below class 10','दसवीं से कम'],['Class 10','दसवीं'],['Class 12','बारहवीं'],['ITI / trade certificate','ITI / ट्रेड प्रमाणपत्र'],['Diploma','डिप्लोमा'],['Graduate','स्नातक'],['Postgraduate','स्नातकोत्तर'],['Other','अन्य']]})+
 field('Skills','Skills, machines, trade or other interests','हुनर, मशीनें, ट्रेड या अन्य रुचियाँ','textarea',false,{full:true,placeholder:t('e.g. Tally, welding, sewing, Excel, CNC, electrical repair…','जैसे टैली, वेल्डिंग, सिलाई, Excel, CNC, बिजली की मरम्मत…')})+
 checks('Work_type','Preferred work type','पसंदीदा काम का प्रकार',[['Full-time','पूर्णकालिक'],['Part-time','अंशकालिक'],['Contract / daily work','ठेका / दिहाड़ी'],['Apprenticeship / training','अप्रेंटिसशिप / प्रशिक्षण'],['Internship','इंटर्नशिप']]));}
 function more(){if(kind==='vendor')return title('Help us make the right introduction.','सही परिचय कराने में मदद करें।','Everything here is optional. You can continue without filling it in.','यहाँ सब वैकल्पिक है। आप बिना भरे आगे बढ़ सकते हैं।')+wrap(
 field('Years_in_business','Years in business','व्यवसाय में कितने वर्ष','select',false,{options:[['Just starting','अभी शुरुआत'],['Under 1 year','1 वर्ष से कम'],['1–3 years','1–3 वर्ष'],['3–5 years','3–5 वर्ष'],['5+ years','5 वर्ष से अधिक']]})+
 field('Team_size','Team size','टीम का आकार','select',false,{options:[['Just me','केवल मैं'],['2–10 people','2–10 लोग'],['11–50 people','11–50 लोग'],['51+ people','51 से अधिक लोग']]})+
 field('Capacity','Capacity / equipment / typical lead time','क्षमता / उपकरण / सामान्य समय','textarea',false,{full:true,placeholder:t('e.g. 2 trucks; 20 workers; 3-day delivery','जैसे 2 ट्रक; 20 कामगार; 3 दिन में डिलीवरी')})+
 field('GST_status','GST registration status','GST पंजीकरण स्थिति','select',false,{options:[['Registered','पंजीकृत'],['Not registered','पंजीकृत नहीं'],['Applied','आवेदन किया है'],['Prefer to discuss','बात करना चाहूँगा']]})+
 field('Website','Website / catalogue link','वेबसाइट / कैटलॉग लिंक','url',false,{placeholder:'https://…'})+
 field('Certifications','Certifications / licences / quality standards','प्रमाणपत्र / लाइसेंस / गुणवत्ता मानक','text',false,{full:true})+
 field('Notes','Experience, client industries or anything else','अनुभव, ग्राहक उद्योग या अन्य जानकारी','textarea',false,{full:true})+attachment());
 return title('A little more about you.','आपके बारे में थोड़ी और जानकारी।','Optional details help us match your profile. Skip anything you prefer.','वैकल्पिक जानकारी सही अवसर ढूँढने में मदद करेगी। चाहें तो छोड़ दें।')+wrap(
 field('Expected_monthly_pay_INR','Expected monthly pay (₹)','अपेक्षित मासिक वेतन (₹)','number',false,{placeholder:t('Or leave blank to discuss','या बातचीत के लिए खाली छोड़ें')})+
 field('LinkedIn','LinkedIn profile link','LinkedIn प्रोफ़ाइल लिंक','url',false,{full:true,placeholder:'https://www.linkedin.com/in/…',hint:t('Optional link only. This does not import your profile.','केवल वैकल्पिक लिंक। इससे प्रोफ़ाइल अपने आप नहीं भरेगी।')})+
 attachment()+
 `<details class="extra"><summary>${t('Add qualifications & work history (optional)','योग्यता और कार्य अनुभव जोड़ें (वैकल्पिक)')}</summary><div class="field-grid">`+
 field('Qualification_trade','Course / trade / specialisation','कोर्स / ट्रेड / विशेषज्ञता')+
 field('Institute','School / college / ITI','स्कूल / कॉलेज / ITI')+
 field('Last_employer','Current / last employer','वर्तमान / पिछली कंपनी')+
 field('Last_role','Current / last job role','वर्तमान / पिछला काम')+
 field('Certifications','Certificates / licences','प्रमाणपत्र / लाइसेंस','text',false,{full:true})+
 field('Notes','Work history, achievements or support needed','कार्य अनुभव, उपलब्धियाँ या ज़रूरी सहायता','textarea',false,{full:true,placeholder:t('Do not include Aadhaar, bank details or other ID numbers.','आधार, बैंक जानकारी या अन्य पहचान संख्या न लिखें।')})+`</div></details>`);
 }
 function attachment(){return field('attachment',kind==='candidate'?'CV / résumé':'Company profile / brochure',kind==='candidate'?'CV / बायोडाटा':'कंपनी प्रोफ़ाइल / ब्रोशर','file',false,{full:true,hint:t('PDF, DOC or DOCX. Up to 5 MB. Avoid identity and bank documents.','PDF, DOC या DOCX। अधिकतम 5 MB। पहचान और बैंक के दस्तावेज़ न दें।')})+(files[kind]?`<div class="field full hint">${t('Selected: ','चुनी गई: ')}${esc(files[kind].name)} <button type="button" id="remove-file" class="button ghost">${t('Remove','हटाएँ')}</button></div>`:'');}
 function review(){
 const rows=Object.entries(values[kind]).filter(([k,v])=>k!=='Consent'&&v!==''&&v!==false&&(!Array.isArray(v)||v.length));
 return title('Check once. Then connect.','एक बार जाँचें। फिर जुड़ें।','Use Back to correct anything before submitting.','जमा करने से पहले सुधार के लिए पीछे जाएँ।')+`<div class="review"><dl>${rows.map(([k,v])=>`<div class="review-row"><dt>${esc(labels[k]?tr(labels[k]):key(k))}</dt><dd>${esc(displayValue(k,v))}</dd></div>`).join('')}${files[kind]?`<div class="review-row"><dt>${t('Attachment','संलग्न फ़ाइल')}</dt><dd>${esc(files[kind].name)}</dd></div>`:''}</dl></div><label class="consent"><input type="checkbox" id="Consent" name="Consent" required ${values[kind].Consent?'checked':''}><span>${t('I agree that Ecotech-12 Industries Association may collect my details, contact me and share them with relevant members for job or business opportunities. I understand that FormSubmit processes this form and any attachment for email delivery, and my registration details are stored in the association organiser’s private Google Sheet. I can request correction or deletion at ecotech12ia@gmail.com.','मैं सहमत हूँ कि ईकोटेक-12 इंडस्ट्रीज़ एसोसिएशन मेरी जानकारी एकत्र कर सकती है, मुझसे संपर्क कर सकती है और नौकरी या व्यवसाय के अवसरों के लिए संबंधित सदस्यों से साझा कर सकती है। मैं समझता/समझती हूँ कि FormSubmit फॉर्म और संलग्न फ़ाइल को ईमेल से पहुँचाने के लिए प्रोसेस करता है। पंजीकरण की जानकारी एसोसिएशन के आयोजक की निजी Google Sheet में भी रखी जाती है। सुधार या जानकारी हटाने के लिए ecotech12ia@gmail.com पर संपर्क कर सकता/सकती हूँ।')} *</span></label><p class="notice">${t('On submission, you may be asked to complete a security check. Please wait for the confirmation page.','जमा करते समय सुरक्षा जाँच पूरी करनी पड़ सकती है। कृपया पुष्टि पेज आने तक प्रतीक्षा करें।')}</p>`;
 }
 const translations=new Map();
 function displayValue(k,v){const convert=x=>lang==='hi'?(translations.get(x)||x):x;return Array.isArray(v)?v.map(convert).join(', '):convert(v);}
 function rememberOptions(){document.querySelectorAll('select option').forEach(o=>{if(lang==='hi')translations.set(o.value,o.textContent)});}
 function render(focus=false){
  $('#fields').innerHTML=[contact,interests,more,review][step]();
  $('#fields').querySelectorAll('[id]').forEach(el=>{if(document.getElementById(el.id+'-hint'))el.setAttribute('aria-describedby',el.id+'-hint')});
  $('#step-caption').textContent=t(`STEP ${step+1} OF 4 · ${steps()[step]}`,`चरण ${step+1} / 4 · ${steps()[step]}`);
  $('#steps').innerHTML=steps().map((s,i)=>`<li class="${i<step?'done':i===step?'current':''}" aria-label="${esc(s)}" ${i===step?'aria-current="step"':''}></li>`).join('');
  $('#back').hidden=step===0;$('#continue').hidden=step===3;$('#submit').hidden=step!==3;$('#form-error').hidden=true;
  if(files[kind]&&$('#attachment')){const dt=new DataTransfer();dt.items.add(files[kind]);$('#attachment').files=dt.files;}
  rememberOptions();
  if(focus) $('.form-title').focus({preventScroll:true});
  $('#Industry')?.addEventListener('change',()=>{capture();values.candidate.Interested_roles=[];render();$('#Industry').focus({preventScroll:true});});
  $('#remove-file')?.addEventListener('click',()=>{capture();files[kind]=null;render();});
  $('#attachment')?.addEventListener('change',()=>{const f=$('#attachment').files[0];if(!f){files[kind]=null;return;}if(f.size>5*1024*1024||!(/\.(pdf|docx?)$/i.test(f.name))){$('#attachment').value='';files[kind]=null;showError(t('Choose a PDF, DOC or DOCX file no larger than 5 MB.','5 MB तक की PDF, DOC या DOCX फ़ाइल चुनें।'));}else{files[kind]=f;$('#form-error').hidden=true;}});
 }
 function showError(msg){$('#form-error').textContent=msg;$('#form-error').hidden=false;}
 function validate(){
  for(const el of $('#fields').querySelectorAll('input,select,textarea')){el.setCustomValidity('');el.removeAttribute('aria-invalid');if(el.type!=='checkbox'&&el.type!=='file'&&el.required&&!el.value.trim())el.setCustomValidity(t('Please complete this field.','कृपया यह जानकारी भरें।'));
   if(el.id==='Mobile'){const digits=el.value.replace(/[\s()+-]/g,'');if(!/^(?:91)?[6-9]\d{9}$/.test(digits))el.setCustomValidity(t('Enter a valid 10-digit Indian mobile number, optionally with +91.','सही 10 अंकों का भारतीय मोबाइल नंबर लिखें; +91 वैकल्पिक है।'));}
   if(el.type==='url'&&el.value){try{const u=new URL(el.value);if(!['https:','http:'].includes(u.protocol))throw Error();if(el.id==='LinkedIn'&&(!/(^|\.)linkedin\.com$/i.test(u.hostname)||!u.pathname.startsWith('/in/')))throw Error();}catch{el.setCustomValidity(t('Enter a valid https:// link'+(el.id==='LinkedIn'?' to your LinkedIn /in/ profile.':'.'),'सही https:// लिंक लिखें'+(el.id==='LinkedIn'?' जिसमें आपकी LinkedIn /in/ प्रोफ़ाइल हो।':'।')));}}
   if(el.id==='email'&&$('#Contact_preference')?.value==='Email'&&!el.value)el.setCustomValidity(t('Add an email address or choose another contact method.','ईमेल पता लिखें या संपर्क का दूसरा माध्यम चुनें।'));
   if(!el.checkValidity()){el.setAttribute('aria-invalid','true');el.closest('details')?.setAttribute('open','');el.focus();showError(t('Please check the highlighted field. ','कृपया चिह्नित जानकारी जाँचें। ')+ (lang==='hi'?'ज़रूरी जानकारी सही रूप में भरें।':el.validationMessage));return false;}
  }return true;
 }
 $('#continue').addEventListener('click',()=>{if(!validate())return;capture();step++;render(true);$('.form-card').scrollIntoView({behavior:'smooth',block:'start'});});
 $('#back').addEventListener('click',()=>{capture();step--;render(true);});
 function selectType(type){capture();kind=type;step=0;document.querySelectorAll('[data-type]').forEach(b=>{b.classList.toggle('active',b.dataset.type===type);b.setAttribute('aria-pressed',String(b.dataset.type===type))});render();}
 document.querySelectorAll('[data-type]').forEach(b=>b.addEventListener('click',()=>selectType(b.dataset.type)));
 document.querySelectorAll('[data-start]').forEach(b=>b.addEventListener('click',()=>selectType(b.dataset.start)));
 $('#language').addEventListener('click',()=>{capture();lang=lang==='en'?'hi':'en';document.documentElement.lang=lang;$('#language').innerHTML=t('हिन्दी <span>↗</span>','English <span>↗</span>');$('#language').setAttribute('aria-label',t('Switch to Hindi','Switch to English'));document.querySelectorAll('[data-i]').forEach(el=>{const pair=E12.ui[el.dataset.i];if(pair)el.innerHTML=tr(pair)});[...E12.sectors,...E12.services,...Object.values(E12.roles).flat(),...E12.commonRoles].forEach(p=>translations.set(...p));render();});
 form.addEventListener('keydown',e=>{if(e.key==='Enter'&&e.target.tagName==='INPUT'&&e.target.type!=='file'){e.preventDefault();if(step<3)$('#continue').click();}});
 form.addEventListener('submit',e=>{e.preventDefault();if(step!==3||!validate())return;capture();if(!navigator.onLine){showError(t('You appear to be offline. Keep this page open, reconnect and try again.','इंटरनेट उपलब्ध नहीं लग रहा है। पेज खुला रखें, इंटरनेट जोड़ें और फिर कोशिश करें।'));return;}
  // Rebuild a native multipart POST from in-memory values; no personal data in URLs or local storage.
  form.querySelectorAll('[data-payload]').forEach(el=>el.remove());
  for(const [k,v] of Object.entries(values[kind])){if(k==='Consent'||v===''||v===false||(Array.isArray(v)&&!v.length))continue;const input=document.createElement('input');input.type='hidden';input.name=key(k);input.value=Array.isArray(v)?v.join('; '):String(v);input.dataset.payload='true';form.append(input);}
  if(files[kind]){const filename=document.createElement('input');filename.type='hidden';filename.name='Attachment name';filename.value=files[kind].name;filename.dataset.payload='true';form.append(filename);const fileInput=document.createElement('input');fileInput.type='file';fileInput.name='attachment';fileInput.hidden=true;fileInput.dataset.payload='true';const dt=new DataTransfer();dt.items.add(files[kind]);fileInput.files=dt.files;form.append(fileInput);}
  $('#Consent').value='Agreed: collect, contact and share with relevant association members; FormSubmit email processing and private Google Sheet storage disclosed.';
  $('#subject').value=`Ecotech 12 Connect | ${kind==='candidate'?'Candidate':'Vendor'} | ${values[kind].Full_name}`;
  $('#registration-type').value=kind==='candidate'?'Candidate':'Vendor';$('#reference').value='E12-'+crypto.randomUUID().slice(0,8).toUpperCase();$('#submitted-at').value=new Date().toISOString();$('#form-language').value=lang==='hi'?'Hindi':'English';
  $('#next-url').value=new URL('thanks.html?lang='+lang,location.href).href;$('#form-url').value=new URL('./',location.href).href;
  $('#submit').disabled=true;$('#submit').textContent=t('Opening secure submission…','सुरक्षित सबमिशन खुल रहा है…');HTMLFormElement.prototype.submit.call(form);
 });
 window.addEventListener('pageshow',()=>{$('#submit').disabled=false;$('#submit').innerHTML=tr(E12.ui.submit)});
 render();
})();
