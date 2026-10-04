(Dev_Formats)=
# Output formats

Ackredit ships with simple renderers in `ackredit.formats`. You can add your own renderer and register it.

Plugins receive the complete bibliography in an independently owned snapshot.
The outer mapping and individual field mappings are read only; nested lists and
dictionaries preserve their types and can be changed locally without affecting
the registry or later reports, even if the renderer subsequently raises.
Built-in formats snapshot only the records they render. The development
`workflow` format instead reads the existing detached attribution payload;
the plugin callable contract remains `renderer(used, items)`.
