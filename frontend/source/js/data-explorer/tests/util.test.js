import * as util from '../util';

describe('util.formatFriendlyPrice()', () => {
  it('should return price w/o cents if price is integral', () => {
    expect(util.formatFriendlyPrice(1)).toBe('1');
  });

  it('should return price w/ cents if price is float', () => {
    expect(util.formatFriendlyPrice(1.1)).toBe('1.10');
  });
});

describe('util.getLastCommaSeparatedTerm()', () => {
  expect(util.getLastCommaSeparatedTerm('foo')).toBe('foo');
  expect(util.getLastCommaSeparatedTerm('foo,bar')).toBe('bar');
  expect(util.getLastCommaSeparatedTerm('foo, bar')).toBe('bar');
  expect(util.getLastCommaSeparatedTerm('foo , bar')).toBe('bar');
  expect(util.getLastCommaSeparatedTerm('foo bar')).toBe('foo bar');
});

describe('util.parseQuery()', () => {
  expect(util.parseQuery('?foo=bar')).toMatchObject({ foo: 'bar' });
  expect(util.parseQuery('?foo=bar&baz=qux')).toMatchObject({ foo: 'bar', baz: 'qux' });
  expect(util.parseQuery('?foo=foo+bar')).toMatchObject({ foo: 'foo bar' });
  expect(util.parseQuery('?foo=foo%20bar')).toMatchObject({ foo: 'foo bar' });
});

describe('util.joinQuery()', () => {
  expect(util.joinQuery({ foo: 'bar', baz: 'quux hi' }))
    .toBe('?foo=bar&baz=quux%20hi');
});
