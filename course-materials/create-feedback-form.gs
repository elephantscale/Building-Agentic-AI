/**
 * create-feedback-form.gs — Building Agentic AI end-of-course feedback form.
 *
 * Companion to create-intro-form.gs. Creates the Google Form AND a linked
 * responses Google Sheet in YOUR Google Drive, in one run.
 *
 * WHEN TO SHARE IT (decided 2026-10-22, first delivery):
 *   Right after Lab 14 (Claude coding assistant) on Day 5 morning — NOT at the
 *   end of the day. Two reasons:
 *     1. Attendance. Day 5 runs to 16:00+ with the capstone; on Zoom people drop
 *        as soon as the last presentation ends. Mid-morning the room is full.
 *     2. Energy. They have just watched an agent read their code, fix a real
 *        bug, and get REFUSED at a human gate. That is the high point of the week.
 *   The cost: it cannot ask about the capstone, which has not happened yet. Ask
 *   that one out loud at the end instead and write the answers down yourself.
 *
 * ANONYMOUS BY DESIGN. No name field and setCollectEmail(false) — unlike the
 * intro form, where you wanted to know who was who. Here you want candour, and
 * the class VMs are locked down so a forced Google sign-in would block people.
 *
 * HOW TO RUN (once per cohort):
 *   1. Go to https://script.google.com  ->  New project.
 *   2. Delete the empty myFunction(), paste this whole file in, Save.
 *   3. Pick "createFeedbackForm" in the function dropdown, click Run.
 *   4. First run only: approve the permission prompt (it creates a Form + Sheet
 *      in your Drive). Your account -> "Advanced" -> "Go to <project> (unsafe)"
 *      -> Allow. This is your own script.
 *   5. Open View -> Logs (or Executions). Copy the THREE URLs it prints and
 *      paste the fill-in link into Zoom chat.
 */

function createFeedbackForm() {
  var COURSE = 'Building Agentic AI';

  var LABS = [
    'Lab 1 — Agent loop / ReAct by hand',
    'Lab 2 — Research assistant',
    'Lab 3 — Reflective summarization',
    'Lab 4 — Python functions to tools',
    'Lab 5 — Email assistant',
    'Lab 6 — RAG over a vector store',
    'Lab 7 — Evaluate & benchmark',
    'Lab 8 — Onboarding assistant',
    'Lab 9 — LangGraph essay writer',
    'Lab 10 — Zapier + Custom GPT',
    'Lab 11 — No-code CRM agent',
    'Lab 12 — Bedrock CRM assistant',
    'Lab 13 — DSPy self-improving agent',
    'Lab 14 — Claude coding assistant',
    'Lab 15 — Voice support agent',
    'Lab 16 — HR governance agent',
  ];

  var form = FormApp.create(COURSE + ' — Course Feedback');
  form.setDescription(
    'Three minutes, and it is anonymous — no name, no sign-in. I read every ' +
    'answer and it decides what I change for the next delivery. Blunt is useful; ' +
    'polite and vague is not.'
  );
  form.setCollectEmail(false);          // locked-down class VMs: no forced sign-in
  form.setProgressBar(true);
  form.setAllowResponseEdits(true);

  // 1. Overall
  form.addScaleItem()
      .setTitle('Overall, how useful was this course to you?')
      .setBounds(1, 5)
      .setLabels('Not useful', 'Extremely useful')
      .setRequired(true);

  // 2. Best lab
  form.addListItem()
      .setTitle('Which lab taught you the most?')
      .setChoiceValues(LABS)
      .setRequired(true);

  // 3. Weakest lab + why
  form.addListItem()
      .setTitle('Which lab was the least useful?')
      .setChoiceValues(LABS.concat(['They were all worth doing']))
      .setRequired(true);

  form.addParagraphTextItem()
      .setTitle('Why that one? What would have made it worth the time?')
      .setHelpText('This is the single most useful box on the form.');

  // 4. Pace
  form.addMultipleChoiceItem()
      .setTitle('Pace of the labs')
      .setChoiceValues([
        'Too slow — I was waiting a lot',
        'About right',
        'Too fast — I was behind and copying',
      ])
      .setRequired(true);

  // 5. Notebooks vs scripts — the Day 3 observation, tested
  form.addMultipleChoiceItem()
      .setTitle('The explore notebooks (explore.ipynb) vs. running the .py scripts')
      .setHelpText('Labs 3, 6, 7, 8, 9 and 13 shipped a notebook as well as a script.')
      .setChoiceValues([
        'I preferred the notebooks',
        'I preferred the scripts',
        'I used both and liked having both',
        'I did not use the notebooks',
      ])
      .setRequired(true);

  form.addParagraphTextItem()
      .setTitle('Why? And should every lab ship a notebook? (optional)');

  // 6. Live/whiteboard segments vs slides — tests a standing bet
  form.addMultipleChoiceItem()
      .setTitle('Several topics were taught live at the whiteboard instead of from slides ' +
                '(RAG, LangGraph, the API comparison). More of that, or less?')
      .setChoiceValues([
        'More live / whiteboard, fewer slides',
        'The balance was about right',
        'Fewer live segments, more slides I can take away',
      ])
      .setRequired(true);

  // 7. The transferable thing
  form.addParagraphTextItem()
      .setTitle('One thing from this week you will actually use at work in the next month')
      .setHelpText('Concrete beats flattering.')
      .setRequired(true);

  // 8. The open box
  form.addParagraphTextItem()
      .setTitle('What would you change about this course? Anything at all.');

  // 9. What was missing
  form.addParagraphTextItem()
      .setTitle('What did you expect to be covered that was not? (optional)');

  // --- Linked responses spreadsheet, in your Drive -------------------------
  var ss = SpreadsheetApp.create(COURSE + ' — Feedback Responses');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  // --- Print the links you need --------------------------------------------
  Logger.log('========================================================');
  Logger.log('FILL-IN link (paste into Zoom chat): ' + form.getPublishedUrl());
  Logger.log('EDIT link (to change the form):      ' + form.getEditUrl());
  Logger.log('RESPONSES Sheet (your record):       ' + ss.getUrl());
  Logger.log('========================================================');
  Logger.log('Share it right after Lab 14, while the room is still full.');
}
