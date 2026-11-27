import { JsonValue } from "../core/types"

/** The JSON shape of a Fleur value type, described by `fleur.core._shape` in Python. */
export type Shape =
  | { kind: "any" }
  | { kind: "null" }
  | { kind: "boolean" }
  | { kind: "integer" }
  | { kind: "number" }
  | { kind: "string" }
  | { kind: "literal"; values: JsonValue[] }
  | { kind: "union"; options: Shape[] }
  | { kind: "list"; item: Shape }
  | { kind: "dict"; value: Shape }
  | { kind: "ref"; name: string }

export type ObjectShape = { kind: "object"; fields: Record<string, Shape> }

export type ShapeSchema = { root: Shape; defs: Record<string, ObjectShape> }

const describe = (value: unknown): string => {
  if (value === null) return "null"
  if (Array.isArray(value)) return "array"
  if (typeof value === "number" && Number.isInteger(value)) return "integer"
  return typeof value
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value)

const allowsNull = (shape: Shape, schema: ShapeSchema): boolean => {
  if (shape.kind === "null" || shape.kind === "any") return true
  if (shape.kind === "union") return shape.options.some((option) => allowsNull(option, schema))
  if (shape.kind === "literal") return shape.values.includes(null)
  return false
}

const expected = (shape: Shape): string => {
  switch (shape.kind) {
    case "literal":
      return `one of ${shape.values.map((value) => JSON.stringify(value)).join(", ")}`
    case "union":
      return shape.options.map(expected).join(" or ")
    case "list":
      return "array"
    case "dict":
    case "ref":
      return "object"
    default:
      return shape.kind
  }
}

/** Return a message locating the first mismatch, or `null` when the value has the shape. */
export const findMismatch = (value: unknown, shape: Shape, schema: ShapeSchema, path: string): string | null => {
  switch (shape.kind) {
    case "any":
      return null
    case "null":
      return value === null ? null : `${path}: expected null, got ${describe(value)}`
    case "boolean":
    case "string":
      return typeof value === shape.kind ? null : `${path}: expected ${shape.kind}, got ${describe(value)}`
    case "number":
      return typeof value === "number" ? null : `${path}: expected number, got ${describe(value)}`
    case "integer":
      return Number.isInteger(value) ? null : `${path}: expected integer, got ${describe(value)}`
    case "literal":
      return shape.values.includes(value as JsonValue) ? null : `${path}: expected ${expected(shape)}, got ${JSON.stringify(value)}`
    case "union":
      return shape.options.some((option) => findMismatch(value, option, schema, path) === null)
        ? null
        : `${path}: expected ${expected(shape)}, got ${describe(value)}`
    case "list": {
      if (!Array.isArray(value)) return `${path}: expected array, got ${describe(value)}`
      for (let index = 0; index < value.length; index++) {
        const mismatch = findMismatch(value[index], shape.item, schema, `${path}[${index}]`)
        if (mismatch !== null) return mismatch
      }
      return null
    }
    case "dict": {
      if (!isRecord(value)) return `${path}: expected object, got ${describe(value)}`
      for (const [key, item] of Object.entries(value)) {
        const mismatch = findMismatch(item, shape.value, schema, `${path}[${JSON.stringify(key)}]`)
        if (mismatch !== null) return mismatch
      }
      return null
    }
    case "ref": {
      const model = schema.defs[shape.name]
      if (!model) return `${path}: unknown shape ${shape.name}`
      if (!isRecord(value)) return `${path}: expected object, got ${describe(value)}`
      for (const [field, fieldShape] of Object.entries(model.fields)) {
        // A field that may be None may also be omitted, as with Pydantic's exclude_none. Fill it
        // with null so that the app reads None rather than undefined.
        if (!(field in value)) {
          if (!allowsNull(fieldShape, schema)) return `${path}.${field}: missing`
          value[field] = null
          continue
        }
        const mismatch = findMismatch(value[field], fieldShape, schema, `${path}.${field}`)
        if (mismatch !== null) return mismatch
      }
      return null
    }
  }
}
