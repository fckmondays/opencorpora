#coding: utf-8

import sys
from time import clock
from StringIO import StringIO

from utils import split_into_sent, get_pos_tags, process_table


def apply_rule(rule, table):
    applied = StringIO()
    for sent in split_into_sent(table):
        sent = sent.lstrip('sent\n').rstrip('\n<')
        tokens = sent.split('\n')
        if len(tokens) == 0:
            continue
        tokens.insert(0, 'sent')
        tokens.append('/sent')
        word_2, tag_2 = 'sent', 'sent'
        try:
            id_1, word_1, tag_1 = tokens[1].split('\t')[0], tokens[1].split('\t')[1], get_pos_tags(tokens[1])
            if word_1.isdigit():
                word_1 = '_N_'
        except:
            pass
        i = 1
        for token in tokens[2:-1]:
            tag = get_pos_tags(token)
            id = token.split('\t')[0]
            try:
                word = token.split('\t')[1]
            except:
                print tokens[i-1]
                raise Exception
            if word.isdigit():
                word = '_N_'
            if tag_1 == rule.tagset:
                gr_list = tokens[i].split('\t')[2:]
                if rule.context_type == 'previous tag':
                    if tag_2 == rule.context:
                        tokens[i] = id + '\t' + word
                        for grammeme in gr_list[:]:
                            if rule.tag not in grammeme:
                                gr_list.remove(grammeme)
                        for grammeme in gr_list:
                            tokens[i] += ('\t' + grammeme + '\t')
                if rule.context_type == 'previous word':
                    if word_2 == rule.context:
                        tokens[i] = id_1 + '\t' + word_1
                        for grammeme in gr_list[:]:
                            if rule.tag not in grammeme:
                                gr_list.remove(grammeme)
                        for grammeme in gr_list:
                            tokens[i] += ('\t' + grammeme + '\t')
                if rule.context_type == 'next tag':
                    if tag == rule.context:
                        tokens[i] = id_1 + '\t' + word_1
                        for grammeme in gr_list[:]:
                            if rule.tag not in grammeme:
                                gr_list.remove(grammeme)
                        for grammeme in gr_list:
                            tokens[i] += ('\t' + grammeme + '\t')
                if rule.context_type == 'next word':
                    if word == rule.context:
                        tokens[i] = id_1 + '\t' + word_1
                        for grammeme in gr_list[:]:
                            if rule.tag not in grammeme:
                                gr_list.remove(grammeme)
                        for grammeme in gr_list:
                            tokens[i] += ('\t' + grammeme + '\t')
            tag_2, tag_1, word_2, word_1, id_1 = tag_1, tag, word_1, word, id
            i += 1
        applied.write('\n'.join(tokens) + '\n')
    return applied.getvalue()


def get_unamb_tags(entries):
    context = ('w-1', 't-1', 'w+1', 't+1')
    for key in entries:
        entry = entries[key]
        for cont_type in context:
            first_tag = entry.keys()[0]
            chosen_tag = first_tag
            chosen_score = 0
            try:
                chosen_cont = entry[entry.keys()[0]][cont_type].keys()[0]
            except:
                pass
            for tag in entry.keys():
                for cont in entry[tag][cont_type].keys():
                    score = entry[tag][cont_type][cont]
                    if score > chosen_score:
                        chosen_score = score
                        chosen_tag = tag
                        chosen_cont = cont.decode('utf-8')
        if chosen_score > 0:
                yield (key, chosen_tag, cont_type, chosen_cont)


def scoring_function(entries, best_rules):
    best_score = 0
    new_rule = []
    rules_scores = {}
    context = ('w-1', 't-1', 'w+1', 't+1')
    for entry in entries:
        value = entries[entry]
        if len(entry) > 4:
            amb_tag = entry
            amb_tag = amb_tag.rstrip('_')
            tags = set(amb_tag.split('_'))
            if len(tags) > 1:
                result_scores = {}
                for tag in tags:
                    for c in context:
                        freqs = [0, 0, 0]
                        for amb_context in value[c]:
                            amb_context.decode('utf-8')
                            local_scores = {0: 0}
                            for unamb_tag in tags:
                                if unamb_tag != tag:
                                    if unamb_tag in entries.keys():
                                        loc_context = entries[unamb_tag][c]
                                        if amb_context in loc_context.keys():
                                            if tag in entries.keys() and \
                                            loc_context[amb_context] > 3:
                                                local_scores[unamb_tag] = float(entries[tag]['freq']) / \
                                                float(entries[unamb_tag]['freq']) * float(loc_context[amb_context])
                                                freqs = [entries[tag]['freq'], entries[unamb_tag]['freq'], loc_context[amb_context]]
                            try:
                                score = entries[tag][c][amb_context] - max(local_scores.values())
                                result_scores[tag][c][amb_context] = [score] + freqs
                                if score > best_score \
                                and [amb_tag, tag, c, amb_context] not in best_rules:
                                    best_score = score
                                    new_rule = [amb_tag, tag, c, amb_context]
                            except:
                                try:
                                    score = entries[tag][c][amb_context] - max(local_scores.values())
                                    result_scores[tag][c] = {amb_context: [score] + freqs}
                                    if score > best_score \
                                    and [amb_tag, tag, c, amb_context] not in best_rules:
                                        best_score = score
                                        new_rule = [amb_tag, tag, c, amb_context]
                                except:
                                    try:
                                        score = entries[tag][c][amb_context] - max(local_scores.values())
                                        result_scores[tag] = {c: {amb_context: [score] + freqs}}
                                        if score > best_score \
                                        and [amb_tag, tag, c, amb_context] not in best_rules:
                                            best_score = score
                                            new_rule = [amb_tag, tag, c, amb_context]
                                    except:
                                        pass
                rules_scores[amb_tag] = result_scores
    return rules_scores, new_rule, best_score


def find_best_rule():
    pass

if __name__ == '__main__':
    start = clock()
    context_freq = get_list_words_pos(sys.stdin.read())
    finish = clock()
    print finish - start
    with open('iter0.txt', 'w') as output:
        for amb_tag in context_freq.keys():
            for context in context_freq[amb_tag].keys():
                if context is not 'freq':
                    for c_variant in context_freq[amb_tag][context].keys():
                        #print c_variant.decode('utf-8')
                        output.write(str(amb_tag).rstrip('_') + '\t' + \
                                     context + '\t' + c_variant + \
                                    '\t' + str(context_freq[amb_tag][context][c_variant]) + '\n')
                else:
                    output.write(str(amb_tag).rstrip('_') + '\t' + 'freq' + \
                                 '\t' + str(context_freq[amb_tag][context]) + '\n')
    print(clock() - finish)
    finish = clock()
    scores = scoring_function(context_freq)
    print(clock() - finish)
    finish = clock()
    with open('iter0_scores.txt', 'w') as output:
        for amb_tag in scores.keys():
            for tag in scores[amb_tag].keys():
                for context in scores[amb_tag][tag].keys():
                    for c_variant in scores[amb_tag][tag][context].keys():
                        output.write(str(scores[amb_tag][tag][context][c_variant][0]) + '\t' + str(amb_tag) + '\t' + tag + \
                                     '\t' + context + '\t' + \
                                     c_variant + '\t' + str(scores[amb_tag][tag][context][c_variant][1:3]) + '\n')
    print(clock() - finish)
