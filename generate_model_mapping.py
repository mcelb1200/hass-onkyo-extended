
import yaml


def generate_mapping():
    try:
        with open('eiscp_commands_filtered.yaml') as f:
            try:
                data = yaml.load(f, Loader=yaml.FullLoader)
            except AttributeError:
                data = yaml.load(f)
    except Exception as e:
        print(f"Error loading YAML: {e}")
        return

    model_sets = data.get('modelsets', {})

    model_to_sets = {}
    for set_name, models in model_sets.items():
        for model in models:
            if model not in model_to_sets:
                model_to_sets[model] = set()
            model_to_sets[model].add(set_name)

    sli_values = data.get('main', {}).get('SLI', {}).get('values', {})

    model_to_source_list = {}

    for model, sets in model_to_sets.items():
        sources = []
        for value_data in sli_values.values():
            names = value_data.get('name')
            if isinstance(names, list):
                source_id = names[0]
            else:
                source_id = names

            required_sets = value_data.get('models')
            if not required_sets:
                continue

            target_set = required_sets

            if target_set in sets:
                sources.append(source_id)

        sources.sort()
        model_to_source_list[model] = tuple(sources)

    unique_source_lists = {}
    source_list_to_id = {}

    counter = 1
    for s_tuple in model_to_source_list.values():
        if s_tuple not in source_list_to_id:
            sid = f"S{counter}"
            source_list_to_id[s_tuple] = sid
            unique_source_lists[sid] = list(s_tuple)
            counter += 1

    print('"""Model to source mapping for Onkyo receivers."""')
    print('# Generated from eiscp-commands.yaml')
    print('# pylint: disable=line-too-long')
    print('')

    print('SOURCE_SETS = {')
    for sid, sources in sorted(unique_source_lists.items(), key=lambda x: int(x[0][1:])): # noqa: E501
        # Split source list into chunks of 5
        chunks = [sources[i:i + 5] for i in range(0, len(sources), 5)]
        print(f'    "{sid}": [')
        for chunk in chunks:
            items = ", ".join([f"'{s}'" for s in chunk])
            print(f'        {items},')
        print('    ],')

    print('}')
    print('')

    print('MODEL_SET_MAPPING = {')
    for model, s_tuple in sorted(model_to_source_list.items()):
        sid = source_list_to_id[s_tuple]
        print(f'    "{model}": "{sid}",')
    print('}')
    print('')

    print('MODEL_SOURCES = {')
    print('    model: SOURCE_SETS[sid] for model, sid in MODEL_SET_MAPPING.items()')
    print('}')

if __name__ == "__main__":
    generate_mapping()
