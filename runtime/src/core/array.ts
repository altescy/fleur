export function sortBy<T>(items: readonly T[], key: (item: T) => number | string, descending: boolean): T[] {
  const keyed = items.map(item => ({ item, key: key(item) }))
  const order = descending ? -1 : 1
  keyed.sort((left, right) => {
    if (left.key < right.key) return -order
    if (left.key > right.key) return order
    return 0
  })
  return keyed.map(entry => entry.item)
}
