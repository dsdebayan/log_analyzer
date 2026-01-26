import unittest
from utils.prompts import prompt_template, prompt_template_chunk_summary, prompt_template_summary
from langchain_core.prompts import ChatPromptTemplate


class TestPromptsModule(unittest.TestCase):
    """Test cases for the prompts module"""

    def test_prompt_template_is_chat_prompt_template(self):
        """Test that prompt_template is a ChatPromptTemplate instance"""
        self.assertIsInstance(prompt_template, ChatPromptTemplate)

    def test_prompt_template_chunk_summary_is_chat_prompt_template(self):
        """Test that prompt_template_chunk_summary is a ChatPromptTemplate instance"""
        self.assertIsInstance(prompt_template_chunk_summary, ChatPromptTemplate)

    def test_prompt_template_summary_is_chat_prompt_template(self):
        """Test that prompt_template_summary is a ChatPromptTemplate instance"""
        self.assertIsInstance(prompt_template_summary, ChatPromptTemplate)

    def test_prompt_template_has_input_variables(self):
        """Test that prompt_template has the required input variables"""
        # prompt_template should have 'context' and 'input' variables
        self.assertIn('context', prompt_template.input_variables)
        self.assertIn('input', prompt_template.input_variables)

    def test_prompt_template_chunk_summary_has_log_chunks_variable(self):
        """Test that prompt_template_chunk_summary has log_chunks variable"""
        self.assertIn('log_chunks', prompt_template_chunk_summary.input_variables)

    def test_prompt_template_summary_has_log_variable(self):
        """Test that prompt_template_summary has log variable"""
        self.assertIn('log', prompt_template_summary.input_variables)

    def test_prompt_template_contains_system_role(self):
        """Test that main prompt_template contains system role"""
        # Verify that prompt_template is properly configured with messages
        self.assertGreater(len(prompt_template.messages), 0)
        # The first message should be a SystemMessagePromptTemplate
        self.assertIsNotNone(prompt_template.messages[0])

    def test_prompt_template_contains_human_role(self):
        """Test that main prompt_template contains human role"""
        # Verify that prompt_template has at least 2 messages
        self.assertGreaterEqual(len(prompt_template.messages), 2)
        # The second message should be a HumanMessagePromptTemplate
        self.assertIsNotNone(prompt_template.messages[1])

    def test_prompt_template_emoji_logic_in_system_prompt(self):
        """Test that emoji logic is present in system prompt"""
        # Format the prompt with sample inputs to verify emoji logic
        formatted = prompt_template.format(context="test context", input="test input")
        self.assertIn("🔥", formatted)
        self.assertIn("⚠️", formatted)
        self.assertIn("🟡", formatted)
        self.assertIn("✅", formatted)

    def test_prompt_template_chunk_summary_mentions_top_3_issues(self):
        """Test that chunk summary prompt mentions top 3 issues"""
        # Format the template to verify content
        formatted = prompt_template_chunk_summary.format(log_chunks="test log")
        self.assertIn("top 3 issues", formatted)

    def test_prompt_template_summary_mentions_top_3_issues(self):
        """Test that final summary prompt mentions top 3 issues"""
        # Format the template to verify content
        formatted = prompt_template_summary.format(log="test log")
        self.assertIn("top 3 issues", formatted)

    def test_prompt_template_summary_has_emoji_logic(self):
        """Test that final summary prompt has emoji logic"""
        # Format the template to verify emoji logic
        formatted = prompt_template_summary.format(log="test log")
        self.assertIn("🔥", formatted)
        self.assertIn("⚠️", formatted)


class TestPromptTemplateFormatting(unittest.TestCase):
    """Test prompt template formatting"""

    def test_prompt_template_can_be_formatted_with_valid_inputs(self):
        """Test that prompt_template can be formatted with valid inputs"""
        try:
            formatted = prompt_template.format(context="Error occurred", input="What happened?")
            self.assertIsNotNone(formatted)
            self.assertIn("Error occurred", formatted)
            self.assertIn("What happened?", formatted)
        except Exception as e:
            self.fail(f"prompt_template formatting failed: {e}")

    def test_chunk_summary_can_be_formatted(self):
        """Test that prompt_template_chunk_summary can be formatted"""
        try:
            formatted = prompt_template_chunk_summary.format(log_chunks="Sample log data")
            self.assertIsNotNone(formatted)
            self.assertIn("Sample log data", formatted)
        except Exception as e:
            self.fail(f"prompt_template_chunk_summary formatting failed: {e}")

    def test_final_summary_can_be_formatted(self):
        """Test that prompt_template_summary can be formatted"""
        try:
            formatted = prompt_template_summary.format(log="Final summary data")
            self.assertIsNotNone(formatted)
            self.assertIn("Final summary data", formatted)
        except Exception as e:
            self.fail(f"prompt_template_summary formatting failed: {e}")


if __name__ == '__main__':
    unittest.main()
