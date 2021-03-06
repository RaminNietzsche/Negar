#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import string

class PersianEditor():
    """
    """
    
    def __init__(self, text):
        """
        """
        self.text = text
        self.fix_dashes = True
        self.fix_three_dots = True
        self.fix_english_quotes = True
        self.fix_hamzeh = True
        self.cleanup_zwnj = False
        self.fix_spacing_for_braces_and_quotes = True
        self.fix_arabic_numbers = True
        self.fix_english_numbers = True
        self.fix_misc_non_persian_chars = True
        self.fix_perfix_spacing = True
        self.fix_suffix_spacing = True
        self.aggresive = True
        self.cleanup_kashidas = True
        self.cleanup_extra_marks = True
        self.cleanup_spacing = True
        self.cleanup_begin_and_end = True
        self.cleanup()
    def cleanup(self):
        """
        
        Arguments:
        - `self`:
        """
        text = self.text

        # replace double dash to ndash and triple dash to mdash
        if self.fix_dashes:
            text = re.sub(ur'-{3}', ur'—', text)
            text = re.sub(ur'-{2}', ur'–', text)
        # replace three dots with ellipsis
        if self.fix_three_dots:
            text = re.sub(ur'\s*\.{3,}', ur'…', text)

        # replace English quotes with their Persian equivalent
        if self.fix_english_quotes:
            text = re.sub(ur"([\"'`]+)(.+?)(\1)", ur'«\2»', text)

        # should convert ه ی to ه
        # The original regex to find was: (\S)(ه[\s]+[ی])(\s)
        # and in python it removes one more letter at first.
        # I mean = 'همهٔ' after this function changed to 'همه‌ی'
        if self.fix_hamzeh:
            #find = re.compile(ur'(ه[\s]+[ی])(\s)', flags = re.U)
            text = re.sub(ur'هٔ',ur'ه‌ی ', text)
        # remove unnecessary zwnj char that are succeeded/preceded by a space
        if self.cleanup_zwnj:
            text = re.sub(ur'\s+|\s+', ur' ', text)

        # character replacement
        # Resource: http://langref.org/ruby+python/search?q=tr&s=go
        persian_numbers = u"۱۲۳۴۵۶۷۸۹۰"
        english_numbers = u"1234567890"
        arabic_numbers  = u"١٢٣٤٥٦٧٨٩٠"
        bad_chars  = u",;%يةك"
        good_chars = u"،؛٪یهک"


        persian_regexp   = u"(%s)" % u"|".join(persian_numbers)
        arabic_regexp    = u"(%s)" % u"|".join(arabic_numbers)
        english_regexp   = u"(%s)" % u"|".join(english_numbers)

        def _sub(match_object, digits):
            return persian_numbers[digits.find(match_object.group(0))]
        def _sub_arabic(match_object):
            return _sub(match_object, arabic_numbers)
        def _sub_english(match_object):
            return _sub(match_object, english_numbers)

        if self.fix_english_numbers:
            text = re.sub(english_regexp, _sub_english, text)
        if self.fix_arabic_numbers:
            text = re.sub(arabic_regexp, _sub_arabic, text)
        if self.fix_misc_non_persian_chars:
            for i in bad_chars:
                text = re.sub(i, good_chars[bad_chars.index(i)], text)

        # should not replace english chars in english phrases
        #
        # I have to look here later

            
        # put zwnj between word and prefix (mi* nemi*)
        # there's a possible bug here: می and نمی could separate nouns and not prefix
        if self.fix_perfix_spacing:
            #find = re.compile(ur"\s+(ن?می)\s+", flags = re.U)
            text = re.sub(ur"\s+(ن?می)\s+",ur' \1‌', text)

        # put zwnj between word and suffix (*tar *tarin *ha *haye)
        # there's a possible bug here: های and تر could be separate nouns and not suffix
        if self.fix_suffix_spacing:
            text = re.sub(ur'\s+(تر(ی(ن)?)?|ها(ی)?)\s+', ur'‌\1 ', text)
            # in case you can not read it: \s+(tar(i(n)?)?|ha(ye)?)\s+

        # -- Aggressive Editing -------------------------------------------------
        if self.aggresive:
            # replace more than one ! or ? mark with just one
            if self.cleanup_extra_marks:
                text = re.sub(ur'(!){2,}', ur'\1', text)
                text = re.sub(ur'(؟){2,}', ur'\1', text)

            # should remove all kashida
            if self.cleanup_kashidas:
                text = re.sub(ur'ـ+', "", text)
            
        # -----------------------------------------------------------------------
        # should fix outside and inside spacing for () [] {} "" «»

        if self.fix_spacing_for_braces_and_quotes:
            text = re.sub(ur'[   ‌]*(\()\s*([^)]+?)\s*?(\))[   ‌]*', ur' \1\2\3 ', text)
            text = re.sub(ur'[   ‌]*(\[)\s*([^)]+?)\s*?(\])[   ‌]*', ur' \1\2\3 ', text)
            text = re.sub(ur'[   ‌]*(\{)\s*([^)]+?)\s*?(\})[   ‌]*', ur' \1\2\3 ', text)
            text = re.sub(ur'[   ‌]*(“)\s*([^)]+?)\s*?(”)[   ‌]*', ur' \1\2\3 ', text)
            text = re.sub(ur'[   ‌]*(«)\s*([^)]+?)\s*?(»)[   ‌]*', ur' \1\2\3 ', text)

        # : ; , ! ? and their persian equivalents should have one space after and no space before
        if self.fix_spacing_for_braces_and_quotes:
            text = re.sub(ur'[ ]+([:;,؛،.؟!]{1} )[   ]*',ur'\1', text)
            text = re.sub(ur'([۰-۹]+):\s+([۰-۹]+)', ur'\1:\2', text)

        # should fix inside spacing for () [] {} "" «»
        if self.fix_spacing_for_braces_and_quotes:
            text = re.sub(ur'(\()\s*([^)]+?)\s*?(\))', ur'\1\2\3', text)
            text = re.sub(ur'(\[)\s*([^)]+?)\s*?(\])', ur'\1\2\3', text)
            text = re.sub(ur'(\{)\s*([^)]+?)\s*?(\})', ur'\1\2\3', text)
            text = re.sub(ur'(“)\s*([^)]+?)\s*?(”)', ur'\1\2\3', text)
            text = re.sub(ur'(«)\s*([^)]+?)\s*?(»)', ur'\1\2\3', text)

        # should replace more than one space with just a single one
        if self.cleanup_spacing:
            text = re.sub(ur'[ ]+', ur' ', text)
            text = re.sub(ur'([\n]+)[   ‌]', ur'\1', text)

        # remove spaces, tabs, and new lines from the beginning and end of file
        if self.cleanup_begin_and_end:
            text.strip()

        print text.encode('utf-8'),

def helpMessage():
    print """Hi, I'm negars virastar!
    you can use me with a command like this:
    ./Virastar.py [FILE-NAME]/[Argumant]
    My Argumants are:
    \t\t--help : show this message
    \n\n\n
    you can use me more effectively with a command like this:
    \t\t$./Virastar.py FILE-NAME > OutPut\n"""
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        helpMessage()
        sys.exit()
    if sys.argv[1].startswith('--'):
        option = sys.argv[1][2:]
        if option == 'help':
            helpMessage()
    else:
        try:
            fileName = sys.argv[1]
            file     = open(fileName)
            while True:
                line = unicode( file.readline(), encoding='utf-8')
                if len(line) == 0:
                    break
                    #print line
                run2 = PersianEditor(line)
        finally:
            file.close()
