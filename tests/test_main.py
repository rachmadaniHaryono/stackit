"""test main func."""
from itertools import product
from unittest import mock

import pytest
from click.testing import CliRunner


@pytest.mark.parametrize(
    'search, stderr, tag, verbose, version',
    product(
        [None, 'search_input'],
        [None, 'stderr_input'],
        [None, 'tag_input'],
        [None, True],
        [None, True],
    )
)
def test_main(search, stderr, tag, verbose, version):
    """test main."""
    argv = []
    no_input_given = search is None and \
        stderr is None and \
        verbose is None and \
        version is None

    if search is not None:
        argv.extend(['--search',  search])
    if stderr is not None:
        argv.extend(['--search', argv])
    if tag is not None:
        argv.extend(['--tag', tag])
    if verbose is not None:
        argv.extend(['--verbose'])
    if version is not None:
        argv.extend(['--version'])
    with mock.patch('stackit.stackit_core.search_verbose') as m_search_verbose, \
            mock.patch('stackit.stackit_core._search') as m_search, \
            mock.patch('stackit.stackit_core.get_term') as m_get_term, \
            mock.patch('stackit.stackit_core.click') as m_click:
        from stackit import stackit_core
        runner = CliRunner()
        # with pytest.raises(ValueError):
        if no_input_given:
            result = runner.invoke(stackit_core.main, argv)
            result_vars = vars(result)
            result_vars.pop('runner')
            result_vars.pop('exc_info')
            result_vars.pop('exception')
            assert result_vars == {
                'output_bytes': b'',
                'exit_code': 1
            }
        else:
            result = runner.invoke(stackit_core.main, argv)
            assert result.exit_code == 0
            if verbose:
                m_search_verbose.assert_called_once_with(m_get_term.return_value)
            elif search or stderr:
                m_search.assert_called_once_with(mock.ANY)
            elif version:
                m_click.echo.assert_called_once_with(
                    'Version {}'.format(stackit_core.VERSION_NUM))
