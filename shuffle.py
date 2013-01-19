#!/usr/bin/env python

import random
from collections import defaultdict

def add_one(x1, x2):
    if x1 == None:
        return False
    return x1 + 1 == x2


def same(x1, x2):
    return x1 == x2


class Deck(object):
    def __init__(self):
        pass

    def features(self):
        pass

    def expanded_features(self):
        return self.features()

    def measure_uniformity(self, verbose=False):
        feature_uniformity = defaultdict(int)
        for feature in self.features():
            if verbose:
                print feature
            last_seen = defaultdict(int)
            distances = defaultdict(list)
            counts = defaultdict(int)
            for i, c in enumerate(self.cards):
                feature_value = c[feature]
                counts[feature_value] += 1
                if feature_value in last_seen:
                    distance = i - last_seen[feature_value]
                    distances[feature_value].append(distance)
                last_seen[feature_value] = i
            for f in distances:
                if verbose:
                    print f, distances[f], len(self.cards) / counts[f]
                distances[f] = [float(x) * counts[f] / len(self.cards)
                        for x in distances[f]]
            ave_distances = dict()
            max_ave = float('-inf')
            min_ave = float('inf')
            averaged_ave = 0
            weighted_average = 0
            for f in distances:
                ave_distance = sum(distances[f]) / len(distances[f])
                if ave_distance > max_ave:
                    max_ave = ave_distance
                if ave_distance < min_ave:
                    min_ave = ave_distance
                averaged_ave += ave_distance
                weighted_average += ave_distance * counts[f]
            averaged_ave /= len(distances)
            weighted_average /= len(self.cards)
            if verbose:
                print 'Weighted average distance:', weighted_average
                print 'Feature-value averaged distance:', averaged_ave
                print 'Max distance:', max_ave
                print 'Min distance:', min_ave
            feature_uniformity[feature] = weighted_average
        return feature_uniformity

    def measure_sequences(self, verbose=False):
        last = dict()
        sequences = defaultdict(list)
        features = self.features()
        if 'Number' in features:
            features.append('Number-run')
        for f in features:
            last[f] = None
        for c in self.cards:
            if verbose:
                print c
            for f in features:
                if f == 'Number-run':
                    comp = add_one
                    f_c = 'Number'
                else:
                    comp = same
                    f_c = f
                if not comp(last[f], c[f_c]):
                    if verbose:
                        print 'Feature %s not the same' % f
                    sequences[f].append(0)
                else:
                    if verbose:
                        print 'Feature %s the same' % f
                last[f] = c[f_c]
                sequences[f][-1] += 1
        averages = defaultdict(int)
        for f in sequences:
            if verbose:
                print sequences[f]
            averages[f] = (float(sum(sequences[f])) / len(sequences[f]),
                    float(max(sequences[f])))
        return averages


class BohnanzaDeck(Deck):
    def __init__(self):
        self.name = 'Bohnanza Deck'
        self.cards = []
        for i in range(24):
            self.cards.append({'Name': 'Coffee Bean'})
        for i in range(22):
            self.cards.append({'Name': 'Wax Bean'})
        for i in range(20):
            self.cards.append({'Name': 'Blue Bean'})
        for i in range(18):
            self.cards.append({'Name': 'Chili Bean'})
        for i in range(16):
            self.cards.append({'Name': 'Stink Bean'})
        for i in range(14):
            self.cards.append({'Name': 'Green Bean'})
        for i in range(12):
            self.cards.append({'Name': 'Soy Bean'})
        for i in range(10):
            self.cards.append({'Name': 'Black Eyed Bean'})
        for i in range(8):
            self.cards.append({'Name': 'Red Bean'})

    def features(self):
        return ['Name']


class PockerDeck(Deck):
    def __init__(self):
        self.name = 'Pocker Deck'
        self.cards = []
        for i in range(1,14):
            self.cards.append({'Suit': 'Spades',
                               'Color': 'Black',
                               'Number': i})
        for i in range(1,14):
            self.cards.append({'Suit': 'Hearts',
                               'Color': 'Red',
                               'Number': i})
        for i in range(1,14):
            self.cards.append({'Suit': 'Clubs',
                               'Color': 'Black',
                               'Number': i})
        for i in range(1,14):
            self.cards.append({'Suit': 'Diamonds',
                               'Color': 'Red',
                               'Number': i})

    def features(self):
        return ['Suit','Color','Number']

    def expanded_features(self):
        return ['Suit','Color','Number', 'Number-run']


def base_shuffle(deck):
    random.shuffle(deck.cards)


def test_randomness(deck_cls, num_runs=1000, verbose=False):
    deck = deck_cls()
    initial_uniformity = deck.measure_uniformity(verbose)
    initial_sequences = deck.measure_sequences(verbose)
    runs = defaultdict(list)
    for i in range(num_runs):
        base_shuffle(deck)
        uniformity = deck.measure_uniformity(verbose)
        sequences = deck.measure_sequences(verbose)
        for f in deck.expanded_features():
            runs[f].append((uniformity[f], sequences[f]))
    print deck.name
    print
    for f in runs:
        print '%s:' % f
        print 'Uniformity:'
        print '%15s: %6.3f' % ('Initial', initial_uniformity[f])
        ave = sum(x[0] for x in runs[f]) / len(runs[f])
        print '%15s: %6.3f' % ('base_shuffle', ave)
        print 'Sequence Length:'
        print '%15s: %6.3f (max: %5.2f)' % ('Initial', initial_sequences[f][0],
                initial_sequences[f][1])
        ave = sum(x[1][0] for x in runs[f]) / len(runs[f])
        max = sum(x[1][1] for x in runs[f]) / len(runs[f])
        print '%15s: %6.3f (max: %5.2f)' % ('base_shuffle', ave, max)
        print
    print '\n'


def main():
    test_randomness(BohnanzaDeck)
    test_randomness(PockerDeck)
    #d = PockerDeck()
    #base_shuffle(d)
    #d.measure_sequences(verbose=True)


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
