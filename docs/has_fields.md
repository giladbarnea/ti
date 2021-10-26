```python
class Entry(HasFields):
	start: XArrow = Field(caster=XArrow.from_formatted)
	end: Optional[XArrow] = Field(caster=XArrow.from_formatted, optional=True)
	notes: Optional[list[Note]] = Field(optional=True)
	tags: Optional[set[str]] = Field(optional=True)

entry = Entry(start=time)
HasFields.__new__(cls, *args: **kwargs):
```

set(vars(object)) == set(dir(object)) == set(object.__dict__)
set(cls.__dict__) == set(vars(cls))
### cls.__dict__ == vars(cls)
__annotations__
__doc__
__fields__
__module__
end
notes
start
tags
timespan

### dir(cls)
// Total:
__delattr__
__ge__
__init_subclass__
...
dict				
end
notes
start
tags
timespan
### cls.__dict__ - object.__dict__
// removes __doc__
__annotations__
__fields__
__module__
end
notes
start
tags
timespan

### cls.__dict__ - object.__dict__ - cls.__class__.__dict__
// removes __doc__ annd __module__
__annotations__
__fields__
end
notes
start
tags
timespan

### dir(cls) - dir(object)
__annotations__
__dict__			+
__fields__
__module__
__weakref__			+
dict				+
end
notes
start
tags
timespan

### cls.__annotations__
end
notes
start
tags

### cls.__fields__
// Good if 100% Fields
end
notes
start
tags
timespan

| Fields | Annotated | cls.__annotations__ | cls.__fields__ |
| ------ | --------- | ------------------- | -------------- |
| 100%   | 100%      | Exact               | Exact          |
| 100%   | partly    | Lacking             | Exact          |
| partly | 100%      |                     | Lacking        |
| partly | partly    |                     |                |

