Feature: CDATA Terminator Tests

  Scenario: Step text with a CDATA terminator ]]>
    Given a step with the text "<![CDATA[value]]>"

  Scenario: Failing step with a CDATA terminator in its message
    Given a step that fails with the message "expected ]]> in the body"

  Scenario: Failing step whose traceback contains a CDATA terminator
    Given a step that fails on a source line containing a CDATA terminator
