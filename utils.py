import unittest
import random
import string


def bencode(data):
  if isinstance(data, int):
    return "i%de" % data
  if isinstance(data, str):
    return "%d:%s" % (len(data), data)
  if isinstance(data, list):
    return "l%se" % ''.join(bencode(x) for x in data)
  if isinstance(data, dict):
    return "d%se" % ''.join('%s%s' % (bencode(x), bencode(data[x])) for x in sorted(data.keys()))
  
  raise TypeError

def bdecode(data):
  '''Main function to decode bencoded data'''
  def _dechunk(chunks):
    try:
      item = chunks.pop()
    except IndexError:
      raise ValueError('Unexpected end of data')
    
    if (item == 'd'): 
      item = chunks.pop()
      h = {}
      while (item != 'e'):
        chunks.append(item)
        if not chunks[-1].isdigit():
          raise ValueError('Non numeric digit')
        key = _dechunk(chunks)
        h[key] = _dechunk(chunks)
        item = chunks.pop()
      return h
    elif (item == 'l'):
      item = chunks.pop()
      list = []
      while (item != 'e'):
        chunks.append(item)
        list.append(_dechunk(chunks))
        item = chunks.pop()
      return list
    elif (item == 'i'):
      item = chunks.pop()
      num = ''
      while (item != 'e'):
        num  += item
        item = chunks.pop()
      return int(num)
    elif item.isdigit():
      num = ''
      while item.isdigit():
        num += item
        item = chunks.pop()
      line = ''
      for i in range(1, int(num) + 1):
        line += chunks.pop()
      return line
  
  chunks = list(data)
  chunks.reverse()
  
  try:
    root = _dechunk(chunks)
  except IndexError:
    raise ValueError
  
  if len(chunks):
    raise ValueError('Extra data')
  return root

class TestBencode(unittest.TestCase):
  def test_int(self):
    self.assertEqual(bencode(1), 'i1e')
    self.assertEqual(bencode(1832), 'i1832e')
    
    self.assertEqual(bencode(3), 'i3e')
    
  def test_str(self):
    self.assertEqual(bencode('abc'), '3:abc')
    self.assertEqual(bencode('aasdfbc'), '7:aasdfbc')
    
    self.assertEqual(bencode('spam'), '4:spam')
  
  def test_list(self):
    self.assertEqual(bencode(['a', 'c', 'e']), 'l1:a1:c1:ee')
    self.assertEqual(bencode([1,2,3]), 'li1ei2ei3ee')
    self.assertEqual(bencode([1,'a',3]), 'li1e1:ai3ee')
    self.assertEqual(bencode([[1,2],['a','b']]), 'lli1ei2eel1:a1:bee')
    
    self.assertEqual(bencode(['spam', 'eggs']), 'l4:spam4:eggse')
    
  def test_dict(self):
    self.assertEqual(bencode({'a':2}), 'd1:ai2ee')
    self.assertEqual(bencode({'b':[1,2]}), 'd1:bli1ei2eee')
    
    self.assertEqual(bencode({'cow':'moo', 'spam':'eggs'}), 'd3:cow3:moo4:spam4:eggse')
    self.assertEqual(bencode({'spam':['a', 'b']}), 'd4:spaml1:a1:bee')
    self.assertEqual(bencode({"publisher":"bob", "publisher-webpage":"www.example.com", "publisher.location":"home" }), 'd9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:homee')
    
  def test_dict_sorting(self):
    self.assertEqual(bencode({'a':1,'c':10,'b':5}), 'd1:ai1e1:bi5e1:ci10ee')
  
  def test_other(self):
    self.assertRaises(TypeError, bencode, self)

class TestBdecode(unittest.TestCase):
  def test_int(self):
    self.assertEqual(1, bdecode('i1e'))
    self.assertEqual(1832, bdecode('i1832e'))
    
    self.assertEqual(3, bdecode('i3e'))
    
  def test_str(self):
    self.assertEqual('abc', bdecode('3:abc'))
    self.assertEqual('aasdfbc', bdecode('7:aasdfbc'))
    
    self.assertEqual('spam', bdecode('4:spam'))
  
  def test_list(self):
    self.assertEqual(['a', 'c', 'e'], bdecode('l1:a1:c1:ee'))
    self.assertEqual([1,2,3], bdecode('li1ei2ei3ee'))
    self.assertEqual([1,'a',3], bdecode('li1e1:ai3ee'))
    self.assertEqual([[1,2],['a','b']], bdecode('lli1ei2eel1:a1:bee'))
    
    self.assertEqual(['spam', 'eggs'], bdecode('l4:spam4:eggse'))
    
  def test_dict(self):
    self.assertEqual({'a':2}, bdecode('d1:ai2ee'))
    self.assertEqual({'b':[1,2]}, bdecode('d1:bli1ei2eee'))
    
    self.assertEqual({'cow':'moo', 'spam':'eggs'}, bdecode('d3:cow3:moo4:spam4:eggse'))
    self.assertEqual({'spam':['a', 'b']}, bdecode('d4:spaml1:a1:bee'))
    self.assertEqual({'publisher':'bob', 'publisher-webpage':'www.example.com', 'publisher.location':'home' }, bdecode('d9:publisher3:bob17:publisher-webpage15:www.example.com18:publisher.location4:homee'))
  
  def test_invalid(self):
    self.assertRaises(ValueError, bdecode, '3:af')
    self.assertRaises(ValueError, bdecode, '3:afeh')
    self.assertRaises(ValueError, bdecode, '3:afed')
    self.assertRaises(ValueError, bdecode, 'iabce')
    self.assertRaises(ValueError, bdecode, 'i1')
    self.assertRaises(ValueError, bdecode, 'lrofle')
    self.assertRaises(ValueError, bdecode, 'di1e3:lole')
    self.assertRaises(ValueError, bdecode, 'what the fuck')
  
  def test_other(self):
    self.assertRaises(TypeError, bdecode, self)
  
  def test_empty(self):
    self.assertRaises(ValueError, bdecode, '')


class TestReciprical(unittest.TestCase):
  def rand_str(self, recursion):
    return ''.join((random.choice(string.ascii_letters) for x in xrange(random.randint(1,30))))
  def rand_int(self, recursion):
    return random.randint(1,1000000)
  def rand_list(self, recursion=3):
    return_list = []
    for x in xrange(random.randint(1,10)):
      return_list.append(self.rand_element(recursion - 1))
    return return_list
  def rand_dict(self, recursion=3):
    return_dict = {}
    for x in xrange(random.randint(1,10)):
      return_dict[self.rand_str(recursion)] = self.rand_element(recursion - 1)
    return return_dict
  def rand_element(self, recursion=3):
    if recursion == 0:
      functions = (self.rand_str, self.rand_int)
    else:
      functions = (self.rand_str, self.rand_int, self.rand_dict, self.rand_list)
    return random.choice(functions)(recursion)
  
  def test_reciprical(self):
    for i in xrange(100):
      element = self.rand_element()
      self.assertEqual(bdecode(bencode(element)), element)

if __name__ == '__main__':
  unittest.main()