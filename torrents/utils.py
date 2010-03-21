def bencode(data):
  if isinstance(data, int):
    return "i%de" % data
  if isinstance(data, str):
    return "%d:%s" % (len(data), data)
  if isinstance(data, unicode):
    return "%d:%s" % (len(data), data.encode('iso-8859-1'))
  if isinstance(data, list):
    return "l%se" % ''.join(bencode(x) for x in data)
  if isinstance(data, dict):
    return "d%se" % ''.join('%s%s' % (bencode(x), bencode(data[x])) for x in sorted(data.keys()))
  
  raise TypeError('Invalid data type: %s' % type(data))

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