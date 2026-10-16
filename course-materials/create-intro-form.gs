/**
 * create-intro-form.gs — Building Agentic AI "Introduce Yourself" intake form.
 *
 * Creates the Google Form (with all questions) AND a linked responses Google
 * Sheet in YOUR Google Drive, in one run. Student answers go straight to the
 * Sheet — no copy/paste-into-chat needed.
 *
 * HOW TO RUN (once per cohort):
 *   1. Go to https://script.google.com  ->  New project.
 *   2. Delete the empty myFunction(), paste this whole file in, Save.
 *   3. Pick "createIntroForm" in the function dropdown, click Run.
 *   4. First run only: approve the permission prompt (it needs to create a
 *      Form + Sheet in your Drive). Choose your account, "Advanced" ->
 *      "Go to <project> (unsafe)" -> Allow. This is your own script.
 *   5. Open View -> Logs (or Executions). Copy the THREE URLs it prints:
 *        - FILL-IN link  -> send this to students
 *        - EDIT link     -> to tweak the form later
 *        - RESPONSES Sheet -> your live record, in your Drive
 *
 * Field set mirrors the sibling developer course (Building-AI-Applications)
 * intake, adapted for agents. setCollectEmail(false) so external students
 * are not forced to sign in with a Google account.
 */

function createIntroForm() {
  var COURSE = 'Building Agentic AI';

  var form = FormApp.create(COURSE + ' — Introduce Yourself');
  form.setDescription(
    'Two minutes so I can teach to who is actually in the room. Your answers go ' +
    'straight to the trainer. No wrong answers — this just helps me pitch the ' +
    'labs and examples at the right level.'
  );
  form.setCollectEmail(false);          // external students: no forced Google sign-in
  form.setProgressBar(true);
  form.setAllowResponseEdits(true);

  // 1. Name
  form.addTextItem()
      .setTitle('Your name')
      .setRequired(true);

  // 2. Role / team
  form.addTextItem()
      .setTitle('Your role / team')
      .setHelpText('e.g. backend engineer, ML engineer, data scientist, tech lead')
      .setRequired(true);

  // 3. Python comfort (1-4 scale)
  form.addScaleItem()
      .setTitle('How comfortable are you with Python?')
      .setBounds(1, 4)
      .setLabels('Rusty / learning', 'I write it daily')
      .setRequired(true);

  // 4. Experience building with LLMs / agents
  form.addMultipleChoiceItem()
      .setTitle('How much have you built with LLMs or agents so far?')
      .setChoiceValues([
        'Not yet — this is my start',
        'I have called an LLM API (OpenAI / Anthropic / etc.)',
        'I have built a RAG or tool-using app',
        'I have built or shipped an agent',
      ])
      .setRequired(true);

  // 5. Which agent tools / frameworks have you tried? (census)
  form.addCheckboxItem()
      .setTitle('Which of these have you tried? (check any)')
      .setChoiceValues([
        'None yet',
        'OpenAI API / Assistants',
        'LangChain or LangGraph',
        'AWS Bedrock',
        'DSPy',
        'Claude API',
        'Zapier / low-code',
        'Google ADK',
      ])
      .showOtherOption(true);

  // 6. A real task you'd want an agent to handle (paragraph)
  form.addParagraphTextItem()
      .setTitle('A real task or workflow from your work you would love an agent to handle')
      .setHelpText('Be concrete — it makes a great running example in class.');

  // 7. Walk-away goal
  form.addTextItem()
      .setTitle('One thing you want to walk away able to do')
      .setRequired(true);

  // 8. Anything to cover (optional)
  form.addParagraphTextItem()
      .setTitle('Anything you especially want covered? (optional)');

  // --- Linked responses spreadsheet, in your Drive -------------------------
  var ss = SpreadsheetApp.create(COURSE + ' — Intro Responses');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  // --- Print the links you need --------------------------------------------
  Logger.log('========================================================');
  Logger.log('FILL-IN link (send to students): ' + form.getPublishedUrl());
  Logger.log('EDIT link (to change the form):  ' + form.getEditUrl());
  Logger.log('RESPONSES Sheet (your record):   ' + ss.getUrl());
  Logger.log('========================================================');
  Logger.log('Tip: in the Form, Responses tab -> ⋮ -> "Get email ' +
             'notifications for new responses" to be pinged on each submit.');
}
