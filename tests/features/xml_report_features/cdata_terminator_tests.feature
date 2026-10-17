Feature: CDATA Terminator Tests

  Scenario: Step text with a CDATA terminator ]]>
    Given a step with the text "<![CDATA[value]]>"

  Scenario: Failing step with a CDATA terminator in its message
    Given a step that fails with the message "expected ]]> in the body"
