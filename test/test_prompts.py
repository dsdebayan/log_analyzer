"""
Unit tests for the prompts module in utils/prompts.py
"""
import pytest
from utils.prompts import prompt_template
from langchain_core.prompts import ChatPromptTemplate


class TestPromptTemplate:
    """Tests for the prompt template configuration"""

    def test_prompt_template_is_chat_prompt_template(self):
        """Test that prompt_template is a ChatPromptTemplate instance"""
        assert isinstance(prompt_template, ChatPromptTemplate)

    def test_prompt_template_has_messages(self):
        """Test that prompt_template has messages configured"""
        assert hasattr(prompt_template, 'messages')

    def test_prompt_template_message_count(self):
        """Test that prompt_template has exactly 2 messages (system and human)"""
        # ChatPromptTemplate should have 2 messages: system and human
        assert len(prompt_template.messages) == 2

    def test_prompt_template_system_message_exists(self):
        """Test that system message is configured"""
        messages = prompt_template.messages
        # Check the class name instead of type attribute
        assert "SystemMessagePromptTemplate" in str(type(messages[0]))

    def test_prompt_template_human_message_exists(self):
        """Test that human message is configured"""
        messages = prompt_template.messages
        # Check the class name instead of type attribute
        assert "HumanMessagePromptTemplate" in str(type(messages[1]))

    def test_prompt_template_system_message_contains_context(self):
        """Test that system message template contains {context} variable"""
        messages = prompt_template.messages
        system_message = messages[0]
        # The template should have context variable
        assert "context" in str(system_message.prompt.template).lower()

    def test_prompt_template_human_message_contains_input(self):
        """Test that human message template contains {input} variable"""
        messages = prompt_template.messages
        human_message = messages[1]
        # The template should have input variable
        assert "input" in str(human_message.prompt.template).lower()

    def test_prompt_template_system_message_contains_analyzer_role(self):
        """Test that system message mentions log analyzer role"""
        messages = prompt_template.messages
        system_message = messages[0]
        template_text = str(system_message.prompt.template)
        assert "log analyzer" in template_text.lower()

    def test_prompt_template_system_message_mentions_emoji(self):
        """Test that system message mentions emoji usage"""
        messages = prompt_template.messages
        system_message = messages[0]
        template_text = str(system_message.prompt.template)
        assert "emoji" in template_text.lower()

    def test_prompt_template_system_message_mentions_concise_response(self):
        """Test that system message asks for concise responses"""
        messages = prompt_template.messages
        system_message = messages[0]
        template_text = str(system_message.prompt.template)
        assert "concise" in template_text.lower() or "limit" in template_text.lower()

    def test_prompt_template_can_be_formatted(self):
        """Test that prompt template can be formatted with context and input"""
        try:
            # This should work without raising an exception
            formatted = prompt_template.format_messages(
                context="Some log context here",
                input="What is the error?"
            )
            assert len(formatted) == 2
            assert formatted[0].type == "system"
            assert formatted[1].type == "human"
        except Exception as e:
            pytest.fail(f"Failed to format prompt template: {e}")

    def test_prompt_template_input_variables(self):
        """Test that prompt template has the expected input variables"""
        # The template should expect 'context' and 'input' variables
        input_vars = prompt_template.input_variables
        assert "context" in input_vars
        assert "input" in input_vars
