import random
import string
import argparse
import os


def load_config(filename):
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Warning: Config file {filename} not found, using defaults")
        return None


def generate_class_name():
    config_prefixes = load_config('prefixes.txt')
    prefixes = config_prefixes if config_prefixes else [
        'Data', 'User', 'Manager', 'Processor', 'Handler',
        'Service', 'Helper', 'Validator', 'Checker', 'Generator'
    ]

    config_suffixes = load_config('suffixes.txt')
    suffixes = config_suffixes if config_suffixes else [
        '', 'Impl', 'Util', 'Controller', 'Factory', 'Adapter'
    ]
    name = random.choice(prefixes)
    if random.random() < 0.5:
        name += random.choice(suffixes)
    if random.random() < 0.3:
        name += str(random.randint(1, 99))
    return name


def generate_field():
    types = [
        ('int', 'i_', lambda: random.randint(1, 100)),
        ('float', 'f_', lambda: round(random.uniform(0.1, 100.0), 2)),
        ('bool', 'b_', lambda: random.choice(['true', 'false']))
    ]
    t_type, t_prefix, t_gen = random.choice(types)
    return (t_type, f"{t_prefix}{random_string(5)}", t_gen)


def random_string(length):
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def generate_constructor(class_name, fields):
    if not fields:
        return ""

    initializers = []
    for t_type, name, generator in fields:
        initializers.append(f"{name}({generator()})")

    return f"public:\n" \
        f"    {class_name}() : {', '.join(initializers)} {{}}\n"


def generate_normal_method(fields):
    config_methods = load_config('normal_methods.txt')
    method_verbs = config_methods if config_methods else [
        'calculate', 'update', 'process', 'handle'
    ]
    method_name = f"{random.choice(method_verbs)}{random_string(4).capitalize()}"
    operations = []

    if fields:
        for _ in range(random.randint(1, 3)):
            field = random.choice(fields)
            op = random.choice([
                f"{field[1]} += {random.randint(1, 10)};",
                f"{field[1]} = {field[2]()};",
                f"{field[1]} *= {random.randint(2, 5)};"
            ])
            operations.append(op)

    return_type = random.choice(['void', 'int', 'float'])
    return_stmt = "return;" if return_type == 'void' else "return 0;" if return_type == 'int' else "return 0.0f;"

    return f"public:\n" \
        f"    {return_type} {method_name}() {{\n" \
        f"        {' '.join(operations)}\n" \
        f"        {return_stmt}\n" \
        f"    }}\n"


def generate_smart_bool_method(fields, existing_methods):
    config_methods = load_config('bool_methods.txt')
    bool_verbs = config_methods if config_methods else [
        'check', 'verify', 'validate'
    ]
    method_name = f"{random.choice(bool_verbs)}{random_string(3).capitalize()}"
    is_public = random.choice([True, False])
    access = "public" if is_public else "private"
    code = [f"{access}:"]
    code.append(f"    bool {method_name}() {{")

    # 40%概率调用现有方法
    if existing_methods and random.random() < 0.4:
        callees = random.sample(existing_methods, min(2, len(existing_methods)))
        code.append(f"        return {' && '.join([f'{c}()' for c in callees])};")
    else:
        # 生成新的验证逻辑
        numeric_fields = [f for f in fields if f[0] in ['int', 'float']]
        if not numeric_fields:
            code.append("        return true;")
        else:
            field = random.choice(numeric_fields)
            var_name = field[1]
            loop_times = random.randint(1, 5)
            loop_var = random.choice(['i', 'j', 'k'])

            # 生成验证算法
            algorithm_type = random.choice(['sum', 'bit', 'product'])
            code.append(f"        int temp = {var_name};")
            code.append(f"        for (int {loop_var}=0; {loop_var}<{loop_times}; ++{loop_var}) {{")

            if algorithm_type == 'sum':
                code.append(f"            temp += {random.randint(1, 5)};")
                condition = "temp > 0"
            elif algorithm_type == 'bit':
                code.append("            temp |= 1;")
                condition = "(temp & 1) == 1"
            else:
                code.append(f"            temp *= {random.randint(2, 5)};")
                condition = "temp != 0"

            code.append("        }")
            code.append(f"        return {condition};")

    code.append("    }")
    return "\n".join(code), method_name


def generate_cpp_class():
    class_name = generate_class_name()
    num_fields = random.randint(2, 5)
    fields = [generate_field() for _ in range(num_fields)]

    code = []
    code.append(f"class {class_name} {{\nprivate:")
    code.append("\n".join([f"    {t} {name};" for t, name, _ in fields]))
    code.append("")
    code.append(generate_constructor(class_name, fields))

    # 生成bool方法
    bool_methods = []
    num_bool_methods = random.randint(3, 5)
    existing_methods = []
    for _ in range(num_bool_methods):
        method_code, method_name = generate_smart_bool_method(fields, existing_methods)
        code.append(method_code)
        existing_methods.append(method_name)

    # 普通方法（排除bool返回类型）
    num_normal_methods = random.randint(2, 4)
    code.extend([generate_normal_method(fields) for _ in range(num_normal_methods)])

    code.append("};\n")
    return "\n".join(code)


def main():
    parser = argparse.ArgumentParser(description='Generate random C++ classes with verification methods')
    parser.add_argument('-n', '--num-classes', type=int, default=100,
                        help='Number of classes to generate (default: 100)')
    parser.add_argument('-o', '--output-dir', type=str, default='gen_classes',
                        help='Output directory path (default: gen_classes)')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    for _ in range(args.num_classes):
        class_code = generate_cpp_class()
        class_name = class_code.split('class ')[1].split(' ')[0].strip()

        header_file = os.path.join(args.output_dir, f"{class_name}.h")

        with open(header_file, 'w', encoding='utf-8') as f:
            f.write(f"#ifndef {class_name.upper()}_H\n")
            f.write(f"#define {class_name.upper()}_H\n\n")
            f.write("#include <cstdint>\n\n")
            f.write(class_code)
            f.write(f"\n#endif // {class_name.upper()}_H\n")

    print(f"Successfully generated {args.num_classes} classes in directory '{args.output_dir}'")


if __name__ == "__main__":
    main()
