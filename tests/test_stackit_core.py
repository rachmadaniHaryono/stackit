"""test module."""
from itertools import product
from unittest import mock

import pytest


def test_config_init():
    """test init."""
    from stackit.stackit_core import Config
    obj = Config()
    vars(obj) == {
        'search': False,
        'stderr': False,
        'tag': False,
        'versbose': False,
    }


@pytest.mark.parametrize(
    'prompt_side_effect',
    [
        ['b', 'q'],
        ['z', 'q'],  # random char input at the beginning
    ]
)
def test_select(prompt_side_effect):
    """test func."""
    q_json_link = mock.Mock()
    question = mock.Mock()
    question.json = {'link': q_json_link}
    questions = [question]
    num = 1
    prompt_msg = 'Enter b to launch browser, x to return to search, or q to quit'
    prompt_msg_error = 'The input entered was not recognized as a valid choice.'
    with mock.patch('stackit.stackit_core.print_full_question') as print_fq, \
            mock.patch('stackit.stackit_core.click') as m_click:
        m_click.prompt.side_effect = prompt_side_effect
        from stackit.stackit_core import select
        with pytest.raises(SystemExit):
            select(questions, num)
        print_fq.assert_called_once_with(questions[0])
        if prompt_side_effect[0] == 'b':
            m_click.assert_has_calls([
                mock.call.prompt(prompt_msg),
                mock.call.launch(q_json_link),
                mock.call.prompt(prompt_msg)
            ])
        elif prompt_side_effect[0] == 'x':
            pass
        else:
            m_click.assert_has_calls([
                mock.call.prompt(prompt_msg),
                mock.call.style(prompt_msg_error, err=True, fg='red'),
                mock.call.echo(m_click.style.return_value),
                mock.call.prompt(prompt_msg)
            ])


@pytest.mark.parametrize('num', [1])
def test_select_func_and_return_to_search(num):
    """test func."""
    q1 = mock.Mock()
    q2 = mock.Mock()
    questions = [q1, q2]
    prompt_side_effect = ['x', 'q']
    with mock.patch('stackit.stackit_core.print_full_question') as print_fq, \
            mock.patch('stackit.stackit_core.click') as m_click, \
            mock.patch('stackit.stackit_core.print_question') as print_q:
        m_click.prompt.side_effect = prompt_side_effect
        from stackit import stackit_core
        stackit_core.NUM_RESULTS = 2
        stackit_core.select(questions, num)
        print_fq.assert_called_once_with(questions[0])
        print_q.assert_has_calls([
            mock.call(q1, 1),
            mock.call(q2, 2),
        ])


@pytest.mark.parametrize(
    'prompt_side_effect',
    [
        ['m'],
        ['q'],
        ['1', 'm'],
        ['z', 'm'],  # random char
    ]
)
def test_focus_question(prompt_side_effect):
    """test func."""
    question = mock.Mock()
    questions = [question]
    prompt_msg = "Enter m for more, a question number to select, or q to quit"
    prompt_msg_error = "The input entered was not recognized as a valid choice."
    first_prompt = prompt_side_effect[0]
    with mock.patch('stackit.stackit_core.click') as m_click, \
            mock.patch('stackit.stackit_core.select') as m_select:
        m_click.prompt.side_effect = prompt_side_effect
        from stackit import stackit_core
        if first_prompt == 'q':
            with pytest.raises(SystemExit):
                stackit_core.focus_question(questions=[question])
        else:
            stackit_core.focus_question(questions=questions)
        if first_prompt == 'm' or first_prompt == 'q':
            pass
        elif first_prompt.isnumeric() and int(first_prompt) <= len(questions):
            m_select.assert_called_once_with(questions, int(first_prompt))
        else:
            m_click.assert_has_calls([
                mock.call.prompt(prompt_msg),
                mock.call.style(prompt_msg_error, err=True, fg='red'),
                mock.call.echo(m_click.style.return_value),
                mock.call.prompt(prompt_msg)
            ])


@pytest.mark.parametrize(
    'questions',
    [
        [],
        [mock.Mock()],
        [mock.Mock(), mock.Mock()],
    ]
)
def test_search(questions):
    """test func."""
    if questions:
        for idx, _ in enumerate(questions):
            # add random number
            questions[idx].json = {'accepted_answer_id': 1234}
    config = mock.Mock()
    with mock.patch('stackit.stackit_core.click'),\
            mock.patch('stackit.stackit_core.so') as m_so, \
            mock.patch('stackit.stackit_core.print_question'),\
            mock.patch('stackit.stackit_core.focus_question'):
        m_so.search_advanced.return_value = questions
        from stackit import stackit_core
        stackit_core.NUM_RESULTS = 2
        if not questions:
            with pytest.raises(SystemExit):
                stackit_core._search(config)
            return
        else:
            stackit_core._search(config)


def test_print_question():
    """test func."""
    question = mock.Mock()
    question.title = 'Random title.'
    question.json = {'accepted_answer_id': 1234}
    count = mock.Mock()
    with mock.patch('stackit.stackit_core.click') as m_click, \
            mock.patch('stackit.stackit_core.h') as m_h, \
            mock.patch('stackit.stackit_core.so'):
        m_h.handle.return_value = 'Random answer'
        m_click.style.return_value = 'Random header.'
        from stackit import stackit_core
        stackit_core.print_question(question, count)


@pytest.mark.parametrize(
    'config_search, raw_output',
    product(
        [True, False],
        ['', 'line1\nline2'],
    )
)
def test_get_term(config_search, raw_output):
    """test func."""
    config = mock.Mock()
    config.search = config_search
    raw_output = ''
    comm_result = [None, raw_output]
    with mock.patch('stackit.stackit_core.click'),\
            mock.patch('stackit.stackit_core.open'),\
            mock.patch('stackit.stackit_core.subprocess') as m_subprocess:
        m_subprocess.Popen.return_value.communicate.return_value = comm_result
        from stackit import stackit_core
        if not config_search:
            with pytest.raises(SystemExit):
                stackit_core.get_term(config)
        else:
            res = stackit_core.get_term(config)
            assert res


def test_print_full_question():
    """test func."""
    question = mock.Mock()
    question.json = {'accepted_answer_id': 1234}
    question.title = 'Question title.'
    with mock.patch('stackit.stackit_core.click') as m_click,\
            mock.patch('stackit.stackit_core.so'),\
            mock.patch('stackit.stackit_core.h') as m_h:
        m_h.handle.side_effect = ['Question text.', 'Answer.']
        m_click.style.return_value = 'Header'
        from stackit import stackit_core
        stackit_core.print_full_question(question)
        m_click.assert_has_calls([
            mock.call.style(
                '\n\n'
                '------------------------------QUESTION-----------------------------------'
                '\n\n'
                'Question title.\n'
                'Question text.',
                fg='blue'
            ),
            mock.call.echo(
                'Header\n'
                '-------------------------------ANSWER------------------------------------'
                'Answer.'
            )
        ])


def test_search_verbose():
    """test func."""
    term = mock.Mock()
    questions = [mock.Mock()]
    with mock.patch('stackit.stackit_core.so') as m_so, \
            mock.patch('stackit.stackit_core.Sort') as m_sort, \
            mock.patch('stackit.stackit_core.print_full_question') as print_fq:
        m_so.search_advanced.return_value = questions
        from stackit import stackit_core
        # run
        stackit_core.search_verbose(term)
        # test
        m_so.search_advanced.assert_called_once_with(q=term, sort=m_sort.Votes)
        print_fq.assert_called_once_with(questions[0])
