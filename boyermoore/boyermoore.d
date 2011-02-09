/// toy implementation of Boyer-Moore algorithm
/// expected input pattern + alphabet + text

import std.stdio;
import std.math;
import std.string;

int max(int a, int b)
{
  return b > a ? b : a;
} 

interface ITextSearchAlgorithm
{
  /// sets pattern and creates the cached data structures
  void compile(string pattern, char[] alphabet);

  /// returns list of indices where pattern starts
  int[] search(string text);
}

class BoyerMoore : ITextSearchAlgorithm
{
  public void compile(string pattern, char[] alphabet)
  {
    mPattern = pattern;
    if (!mPattern.length)
      return;

    prepareGoodSuffixTable();
    prepareBadCharTable(alphabet);
  }

  public int[] search(string text)
  {
    int[] results;
    results.length = 0;
    // number of comparisons taken by algorithm
    int steps = 0;

    if (text.length < mPattern.length || !mPattern.length)
      return [];

    int patLen = mPattern.length;
    // iterator through text
    int index = patLen;

    // every iteration consists of
    // 1) determining if we have a match
    // 2) shifting the text by offset
    while(index <= text.length)
    {
      // slice window we see from the text
      string slice = text[index - patLen .. index];
      // how much we move in this step
      int offset = 1;
      bool found = true;
      
      assert(slice.length == mPattern.length);
      for (int i = slice.length - 1; i >= 0; i--)
      {
        steps++;
        bool charEquals = slice[i] == mPattern[i];

        if (!charEquals)
        {
          // determine offset 
          offset = max(mGoodSuffixTable[i], mBadCharTable[slice[i]] - (slice.length - 1 - i));
          offset = max(offset, 1);
          found = false;
          break;
        }
      }
      
      if (found)
        results ~= index - patLen;

      index += offset;
    }

    debug
    { 
      printSearchResults(mPattern, text, results);
      writefln("taken %d steps", steps);
    }

    return results;
  }

  private void prepareGoodSuffixTable()
  {
    auto patLen = mPattern.length;
    mGoodSuffixTable = new int[patLen];
    // position indicates the shift
    // if there is unequality between pattern and text on pos i

    mGoodSuffixTable[patLen - 1] = 1;
    GoodSuffixFill:
    for (int i = patLen - 2; i >= 0; i--)
    {
      int offset = 0;
      char notMatch = mPattern[i];
      string slice = mPattern[(i + 1) .. $];

      // find the good suffix inside pattern
      int j;
      for (j = patLen - 1; j > slice.length; j--)
      {
        if (slice == mPattern[j - slice.length .. j] && 
            mPattern[j - slice.length - 1] != notMatch)
        {
          // found an offset
          mGoodSuffixTable[i] = patLen - j;
          continue GoodSuffixFill;
        }
      }

      // special case for the beginning
      // no offset found yet - continue from j down 
      // to check any suffix match with the beginning 
      assert(j == slice.length);
      for (; j > 0; j--)
      { 
        if (slice[$ - j .. $] == mPattern[0 .. j])
        {
          mGoodSuffixTable[i] = patLen - j;
          continue GoodSuffixFill;
        }
      }
      
      mGoodSuffixTable[i] = patLen;
    }
  }

  private void prepareBadCharTable(char[] alphabet)
  {
    // TODO better
    foreach(key; mBadCharTable.keys) 
      mBadCharTable.remove(key);
    foreach (c; alphabet)
      mBadCharTable[c] = mPattern.length;
    for (int i = mPattern.length - 2; i >= 0; i--)
      if (mBadCharTable[mPattern[i]] == mPattern.length)
        mBadCharTable[mPattern[i]] = mPattern.length - 1 - i; 
  }

  private string mPattern;
  private int[] mGoodSuffixTable;
  private int[char] mBadCharTable;

  unittest
  {
    testPrepareGoodSuffixTable();
    testPrepareBadCharTable();
    testSearch();
  }

  static void testPrepareGoodSuffixTable()
  {
    BoyerMoore bm = new BoyerMoore;
    bm.compile("ananas", cast(char[])"ansx");
    assert(bm.mGoodSuffixTable.length == 6);
    assert(bm.mGoodSuffixTable[$ - 1] == 1);
    foreach(i, e; bm.mGoodSuffixTable[0 .. $ - 1])
      assert(e == 6, format("goodSuffixTable[%s] == %s", i, e));

    bm = new BoyerMoore;
    bm.compile("anpanman", cast(char[])"anpm");
    assert(bm.mGoodSuffixTable.length == 8);
    assert(bm.mGoodSuffixTable[$ - 1] == 1);
    assert(bm.mGoodSuffixTable[$ - 2] == 8);
    assert(bm.mGoodSuffixTable[$ - 3] == 3);
    foreach(i, e; bm.mGoodSuffixTable[0 .. $ - 3])
      assert(e == 6, format("goodSuffixTable[%s] == %s", i, e));
  }

  static void testPrepareBadCharTable()
  {
    BoyerMoore bm = new BoyerMoore;
    bm.compile("ananas", cast(char[])"ansx");
    assert(bm.mBadCharTable.length == 4);
    assert(bm.mBadCharTable['a'] == 1);
    assert(bm.mBadCharTable['n'] == 2);
    assert(bm.mBadCharTable['s'] == 6);
    assert(bm.mBadCharTable['x'] == 6);
  }

  static void testSearch()
  {
    BoyerMoore bm = new BoyerMoore;
    // TODO dynamic alphabet
    bm.compile("ananas", cast(char[])"ankupslm");

    int[] results;
    results = bm.search("ananakupslaananassama");
    assert(results.length == 1);
    assert(results[0] == 11);

    results = bm.search("");
    assert(results.length == 0);

    results = bm.search("annna");
    assert(results.length == 0);

    results = bm.search("anananasananas");
    assert(results.length == 2);
    assert(results[0] == 2);
    assert(results[1] == 8);

    results = bm.search("mnanasunas");
    assert(results.length == 0);

    bm = new BoyerMoore;
    // TODO dynamic alphabet
    bm.compile("anpanman", cast(char[])"anpmc");

    results = bm.search("apacmanapanama");
    assert(results.length == 0);

    // overlapping occurence
    results = bm.search("anpanpanmanpanman");
    assert(results.length == 2);
    assert(results[0] == 3);
    assert(results[1] == 9);
  }
}

void printSearchResults(string pattern, string text, int[] results)
{
  char[] getWs(int len)
  {
    char[] ws;
    ws.length = len;
    ws[] = ' ';
    return ws;
  }

  int patLen = pattern.length;

  writeln("===========");
  foreach (index; results)
  {
    writefln("found match at %d", index);
    writefln("%s", text);
    writefln("%s^%s^", getWs(index), getWs(patLen - 1));
  } 
  if (!results.length)
  {
    writefln("no match found");
    writefln("%s", text);
  }
}

void main()
{}

