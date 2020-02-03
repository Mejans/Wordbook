"""
reo_base contains the shared code between the Qt5 and Gtk3 frontends.

reo_base is a part of Reo. It contains a few functions that are reusable across
both the UIs.
"""

import re
import html
import os
import subprocess
from reo import utils


def fold_gen():
    """Make required directories if they don't already exist."""
    if not os.path.exists(utils.CONFIG_FOLD):  # check for Reo folder
        os.makedirs(utils.CONFIG_FOLD)  # create Reo folder
    if not os.path.exists(utils.CDEF_FOLD):  # check Custom Definitions folder.
        os.makedirs(utils.CDEF_FOLD)  # create Custom Definitions folder.


def def_processor(definition, term, sen_col, word_col, markup='html', debug=False):
    """Format the definition obtained from 'dict'."""
    definition = definition.replace('1 definition found\n\nFrom WordNet (r) 3.0 (2006) [wn]:\n', '')
    definition = definition.replace('1 definition found\n\nFrom WordNet (r) 3.1 (2011) [wn]:\n', '')
    definition = html.escape(definition, False)
    try:
        term_in_wn = re.search("  " + term, definition, flags=re.IGNORECASE).group(0)
    except Exception as ex:
        term_in_wn = term
        print("Regex search failed" + str(ex))
    definition = definition.replace(term_in_wn + '\n', '')
    if debug is True:
        print(f"Searching {term_in_wn.strip()}")
    re_list = {r'[ \t\r\f\v]+n\s+': f'<b>{term_in_wn}</b> ~ <i>noun</i>:\n      ',
               r'[ \t\r\f\v]+adv\s+': f'<b>{term_in_wn}</b> ~ <i>adverb</i>:\n      ',
               r'[ \t\r\f\v]+adj\s+': f'<b>{term_in_wn}</b> ~ <i>adjective</i>:\n      ',
               r'[ \t\r\f\v]+v\s+': f'<b>{term_in_wn}</b> ~ <i>verb</i>:\n      ',
               r'([-]+)\s+      \s+': r'\1',
               r'\s+      \s+': r' ',
               r'"$': r'</font>',
               r'\s+(\d+):\D': r'\n  <b>\1:  </b>',
               r'";\s*"': f'</font><b>;</b> <font color="{sen_col}">',
               r'[;:]\s*"': fr'\n        <font color="{sen_col}">',
               r'"\s+\[': r'</font>[',
               r'\[syn:': r'\n        <i>Synonyms: ',
               r'\[ant:': r'\n        <i>Antonyms: ',
               r'}\]': r'}</i>',
               r"\{([^{]*)\}": fr'<font color="{word_col}">\1</font>',
               r'";[ \t\r\f\v]*$': r'</font>',
               r'";[ \t\r\f\v]+(.+)$': r'</font> \1',
               r'"[; \t\r\f\v]+(\(.+\))$': r'</font> \1',
               r'"\s*\-+\s*(.+)\s*([<]*)': r"</font> - \1; \2",
               r';\s*$': r''}
    for x, y in re_list.items():
        re_clean = re.compile(x, re.MULTILINE)
        definition = re_clean.sub(y, definition)
    if markup == "pango":
        definition = definition.replace('<font color="', '<span foreground="')
        definition = definition.replace('</font>', '</span>')
    if not definition.find("`") == -1:
        definition = definition.replace("`", "'")
    if not definition.find("thunder started the sleeping") == -1:
        definition = definition.replace("thunder started the sleeping", "thunder started, the sleeping")
    if markup == "html":
        clean_definition = definition.strip().replace('\n', '<br>')
    else:
        clean_definition = definition.strip()
    return clean_definition


def cls_fmt(clp, text):
    """Format the similar words list obtained."""
    sub_dict = {r'\s+      \s+': r'  ',
                f'  ["]*{text.lower()}["]*$': r'',
                f"(.)  {text.lower()}  (.)": r"\1  \2",
                f'wn: ["]*{text.lower()}["]*  (.)': r"\1",
                f'(.)  "{text.lower()}"  (.)': r"\1  \2",
                r'\s*\n\s*': r'  ',
                r"\s\s+": r", ",
                f'["]+{text.lower()}["]+': r"",
                'wn:[,]*': r''}
    for x, y in sub_dict.items():
        sub_re = re.compile(x)
        clp = sub_re.sub(y, clp).strip()
    clp = clp.rstrip()
    return clp


def fortune():
    """Present fortune easter egg."""
    try:
        fortune_process = subprocess.Popen(["fortune", "-a"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        fortune_process.wait()
        ft = fortune_process.stdout.read().decode()
        ft = html.escape(ft, False)
        return "<tt>" + ft + "</tt>"
    except Exception as ex:
        ft = "Easter Egg Fail!!! Install 'fortune' or 'fortunemod'."
        print(f"{ft}\n{str(ex)}")
        return f"<tt>{ft}</tt>"


def cowfortune():
    """Present cowsay version of fortune easter egg."""
    try:
        cowsay = subprocess.Popen(["cowsay", fortune()], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        cowsay.wait()
        if cowsay:
            cst = cowsay.stdout.read().decode()
            return f"<tt>{cst}</tt>"
        else:
            return "<tt>Cowsay fail... Too bad...</tt>"
    except Exception as ex:
        ft = "Easter Egg Fail!!! Install 'fortune' or 'fortunemod' and also 'cowsay'."
        print(f"{ft}\n{str(ex)}")
        return f"<tt>{ft}</tt>"


def data_obtain(term, word_col, sen_col, markup='html', debug=False):
    """
    Obtain the data to be processed and presented.

    Too complex according to McCabe complexity check. Needs work.
    """
    strategy = "lev"
    try:
        process_def = subprocess.Popen(["dict", "-d", "wn", term], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process_pron = subprocess.Popen(["espeak-ng", "-ven-uk-rp", "--ipa", "-q", term], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        process_close = subprocess.Popen(["dict", "-m", "-d", "wn", "-s", strategy, term], stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
    except Exception as ex:
        print("Didn't Work! ERROR INFO: " + str(ex))
        return
    process_def.wait()
    definition = process_def.stdout.read().decode()
    if not definition == '':
        clean_def = def_processor(definition, term, sen_col, word_col, markup, debug)
        no_def = 0
    else:
        clean_def = f"Couldn't find definition for '{term}'."
        no_def = 1
    process_pron.wait()
    pron = process_pron.stdout.read().decode()
    clean_pron = " /{0}/".format(pron.strip().replace('\n ', ' '))
    process_close.wait()
    close = process_close.stdout.read().decode()
    clean_close = cls_fmt(close, term)
    fail = False
    if term.lower() == 'recursion':
        clean_close = 'recursion'
    if clean_close.strip() == '':
        fail = True
    if process_pron and not no_def == 1:
        final_pron = f"<b>Pronunciation</b>: <b>{clean_pron}</b>"
    else:
        final_pron = "Pronunciation processing failed. Report this as a bug."
    if not fail:
        if no_def == 1:
            final_close = f'<b>Did you mean</b>:<br><i><font color="{word_col}">  {clean_close}</font></i>'
        else:
            final_close = f'<b>Similar Words</b>:<br><i><font color="{word_col}">  {clean_close}</font></i>'
    else:
        final_close = ''
    if markup == "pango":
        data = f'{final_pron.strip()}\n{clean_def}\n{final_close.strip()}'
        data = data.replace('<font color="', '<span foreground="')
        data = data.replace('</font>', '</span>')
        data = data.replace('<br>', '\n')
        final_data = data.replace('&', '&amp;')
    else:
        data = f"<p>{final_pron}</p><p>{clean_def}</p><p>{final_close.strip()}</p>"
        final_data = data.replace('&', '&amp;').replace('  ', '&nbsp;&nbsp;')
    return final_data


def wn_ver_check():
    """Check version of WordNet."""
    try:
        check_process = subprocess.Popen(["dict", "-d", "wn", "test"],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT)
        check_out = check_process.stdout.read().decode()
    except Exception as ex:
        print("Error with dict. Error")
        print(ex)
        return '3.1'
    if not check_out.find('1 definition found\n\nFrom WordNet (r) 3.1 (2011) [wn]:\n') == -1:
        return '3.1'
    elif not check_out.find('1 definition found\n\nFrom WordNet (r) 3.0 (2006) [wn]:\n') == -1:
        return '3.0'


def verinfo():
    """Present clear version info."""
    print('Reo - ' + utils.VERSION)
    print('Copyright 2016-2020 Mufeed Ali')
    print()
    wn_ver = wn_ver_check()
    if wn_ver == '3.1':
        print("WordNet Version 3.1 (2011) (Installed)")
    elif wn_ver == '3.0':
        print("WordNet Version 3.0 (2006) (Installed)")
    print()
    try:
        dict_process = subprocess.Popen(["dict", "-V"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        dict_out = dict_process.stdout.read().decode()
        print(dict_out.strip())
    except Exception as ex:
        print("Looks like missing components. (dict)\n" + str(ex))
    print()
    try:
        espeak_process = subprocess.Popen(["espeak-ng", "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        espeak_process.wait()
        espeak_out = espeak_process.stdout.read().decode()
        print(espeak_out.strip())
    except Exception as ex:
        print("You're missing a few components. (espeak-ng)\n" + str(ex))


def html_to_pango(data):
    """Convert HTML data to Pango markup data. Not a real converter."""
    data = data.replace('<font color="', '<span foreground="')
    data = data.replace('</font>', '</span>')
    data = data.replace('<br>', '\n')
    return data


def read_term(text, speed):
    """Say text loudly."""
    with open(os.devnull, 'w') as NULL_MAKER:
        subprocess.Popen(["espeak-ng", "-ven-uk-rp", "-s", speed, text], stdout=NULL_MAKER, stderr=subprocess.STDOUT)
