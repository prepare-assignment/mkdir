# mkdir

Make a directory.

## Example

```yml
- name: Create image dir
  uses: mkdir
  with:
    directory: out/images
    parents: true
```

## Options

The following options are available:

```yaml
directory:
  description: The directory to create
  type: string
  required: true
parents:
  description: Make parent directories if needed
  required: false
  type: boolean
  default: false
```