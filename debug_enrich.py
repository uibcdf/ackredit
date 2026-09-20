from flowcite import Registry, enrich_all, register_item

register_item(id="test", doi="10.1038/nmeth.1618")
print(f"Before: {Registry.items['test']}")
enrich_all()
print(f"After: {Registry.items['test']}")
