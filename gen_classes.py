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
    name += random.choice(suffixes)
    name += random_string(3).capitalize()
    name += str(random.randint(1, 1000))
    return name


def generate_field():
    types = [
        ('int', 'i_', lambda: random.randint(1, 100)),
        ('double', 'f_', lambda: round(random.uniform(0.1, 100.0), 2)),
        ('bool', 'b_', lambda: random.choice(['true', 'false'])),
        ('int32_t', 'i32_', lambda: random.randint(1, 1000)),
        ('uint32_t', 'u32_', lambda: random.randint(1, 1000)),
        ('int64_t', 'i64_', lambda: random.randint(100, 10000)),
        ('uint64_t', 'u64_', lambda: random.randint(1000, 99999)),
    ]
    t_type, t_prefix, t_gen = random.choice(types)
    return (t_type, f"{t_prefix}{random_string(7)}", t_gen)


def random_string(length):
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def generate_constructor(class_name, fields, existing_methods):
    if not fields:
        return ""

    initializers = []
    for t_type, name, generator in fields:
        initializers.append(f"{name}({generator()})")

    constructor_body = ""
    if existing_methods and random.random() < 0.5:
        callee = random.choice(existing_methods)
        constructor_body = f"\n        {callee}();"

    return f"public:\n" \
        f"    {class_name}() : {', '.join(initializers)} {{{constructor_body}\n    }}\n"


def generate_normal_method(fields, existing_methods):
    config_methods = load_config('normal_methods.txt')
    method_verbs = config_methods if config_methods else [
        'calculate', 'update', 'process', 'handle'
    ]
    method_name = f"{random.choice(method_verbs)}{random_string(4).capitalize()}"
    operations = []

    if existing_methods and random.random() < 0.3:
        callee = random.choice(existing_methods)
        operations.append(f"{callee}();")

    for _ in range(random.randint(1, 3)):
        field = random.choice(fields)
        fname = field[1]
        op = f"{fname} = !{fname};" if fname.startswith('b_') else random.choice([
            f"{fname} += {random.randint(1, 10)};",
            f"{field[1]} = {field[2]()};",
            f"{field[1]} *= {random.randint(2, 5)};"
        ])
        operations.append(op)

    return_type = random.choice(['void', 'int', 'int32_t', 'uint32_t', 'int64_t', 'uint64_t', 'double'])
    return_value = f"{return_type}({random.choice(fields)[1]})"
    return_stmt = "return;" if return_type == 'void' else f"return {return_value};"

    return f"public:\n" \
        f"    {return_type} {method_name}() {{\n" \
        f"        {' '.join(operations)}\n" \
        f"        {return_stmt}\n" \
        f"    }}\n", method_name


def generate_smart_bool_method(fields, existing_methods):
    config_methods = load_config('bool_methods.txt')
    bool_verbs = config_methods if config_methods else [
        'check', 'verify', 'validate'
    ]
    method_name = f"{random.choice(bool_verbs)}{random_string(5).capitalize()}"
    code = [f"public:"]
    code.append(f"    bool {method_name}() {{")

    # 40%概率调用现有方法
    if existing_methods and random.random() < 0.4:
        callees = random.sample(existing_methods, min(2, len(existing_methods)))
        code.append(f"        return {' && '.join([f'{c}()' for c in callees])};")
    else:
        # 生成新的验证逻辑
        numeric_fields = [f for f in fields if f[0] in ['int', 'int32_t', 'uint32_t', 'int64_t', 'uint64_t', 'double']]
        if not numeric_fields:
            code.append("        return true;")
        else:
            field = random.choice(numeric_fields)
            var_name = field[1]
            loop_times = random.randint(1, 5)
            loop_var = random.choice(['i', 'j', 'k'])

            # 生成验证算法
            algorithm_type = random.choice(['sum', 'bit', 'product',
                                            'bit_parity',
                                            'prime_check',
                                            'mod_chain',
                                            'bit_rotation',
                                            'checksum',
                                            'binary_palindrome'])
            int_type = random.choice(['int', 'int32_t', 'uint32_t', 'int64_t', 'uint64_t'])
            code.append(f"        auto temp = {int_type}({var_name});")
            code.append(f"        for (int {loop_var}=0; {loop_var}<{loop_times}; ++{loop_var}) {{")

            condition = "true"
            if algorithm_type == 'sum':
                code.append(f"            temp += {random.randint(1, 5)};")
                condition = "temp > 0"
            elif algorithm_type == 'bit':
                code.append("            temp |= 1;")
                condition = "(temp & 1) == 1"
            elif algorithm_type == 'bit_parity':
                code.append(f"            int bits = 0;")
                code.append(f"            for(auto t = temp; t != 0; t >>= 1) {{")
                code.append(f"                bits += t & 1;")
                code.append(f"            }}")
                code.append(f"            return (bits % 2) == 0 || (bits % 2) == 1;")
            elif algorithm_type == 'prime_check':
                code.append(f"            if(temp < 2) return true;")
                code.append(f"            for({int_type} d=2; {int_type}(d*d)<=temp; ++d) {{")
                code.append(f"                if(temp % d == 0) return true;")
                code.append(f"            }}")
                code.append(f"            return true;")
            elif algorithm_type == 'mod_chain':
                mod1 = random.choice([3, 4, 5])
                mod2 = random.choice([2, 3])
                code.append(f"            temp = (temp % {mod1}) % {mod2};")
                code.append(f"            return temp == temp;")
            elif algorithm_type == 'bit_rotation':
                shift = random.randint(1, 3)
                code.append(f"            temp = (temp << {shift}) | (temp >> (32-{shift}));")
                code.append(f"            return (temp | 0x{random.randint(1, 255):X}) != 0;")
            elif algorithm_type == 'checksum':
                code.append(f"            {int_type} sum = 0;")
                code.append(f"            while(temp > 0) {{")
                code.append(f"                sum += temp % 10;")
                code.append(f"                temp /= 10;")
                code.append(f"            }}")
                code.append(f"            return sum == sum;")
            elif algorithm_type == 'binary_palindrome':
                code.append(f"            {int_type} original = temp;")
                code.append(f"            {int_type} reversed = 0;")
                code.append(f"            while(temp > 0) {{")
                code.append(f"                reversed = (reversed << 1) | (temp & 1);")
                code.append(f"                temp >>= 1;")
                code.append(f"            }}")
                code.append(f"            return original == original;")
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

    # 普通方法
    existing_normal_methods = []
    num_normal_methods = random.randint(2, 4)
    for _ in range(num_normal_methods):
        method_code, method_name = generate_normal_method(fields, existing_normal_methods)
        code.append(method_code)
        existing_normal_methods.append(method_name)

    # 构造
    code.append(generate_constructor(class_name, fields, existing_normal_methods))

    # 生成bool方法
    num_bool_methods = random.randint(3, 5)
    existing_methods = []
    for _ in range(num_bool_methods):
        method_code, method_name = generate_smart_bool_method(fields, existing_methods)
        code.append(method_code)
        existing_methods.append(method_name)

    code.append("};\n")
    return "\n".join(code), existing_methods


def main():
    parser = argparse.ArgumentParser(description='Generate random C++ classes with verification methods')
    parser.add_argument('-n', '--num-classes', type=int, default=100,
                        help='Number of classes to generate (default: 100)')
    parser.add_argument('-o', '--output-dir', type=str, default='gen_classes',
                        help='Output directory path (default: gen_classes)')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    all_headers = []
    for _ in range(args.num_classes):
        class_code, bool_methods = generate_cpp_class()
        class_name = class_code.split('class ')[1].split(' ')[0].strip()

        hname = f"{class_name}.h"
        header_file = os.path.join(args.output_dir, hname)
        all_headers.append((hname, bool_methods))

        with open(header_file, 'w', encoding='utf-8') as f:
            f.write(f"#ifndef {class_name.upper()}_H\n")
            f.write(f"#define {class_name.upper()}_H\n\n")
            f.write("#include <cstdint>\n\n")
            f.write(class_code)
            f.write(f"\n#endif // {class_name.upper()}_H\n")

    # 生成测试用cpp文件
    generate_test_cpp(args.output_dir, all_headers)

    print(f"Successfully generated {args.num_classes} classes in directory '{args.output_dir}'")


def generate_test_cpp(output_dir, headers: list[tuple[str, list[str]]]):
    test_code = [
        "#include <cassert>",
        "#include <vector>",
        "#include <memory>\n"
    ]

    for h, _ in headers:
        test_code.append(f"#include \"{h}\"")

    test_code.append("""
int main() {
""")

    for h, bms in headers:
        class_name = h[:-2]  # 移除.h后缀
        test_code.append(f"""
    {{
        {class_name} c;
    """)
        for bm in bms:
            test_code.append(f"        assert(c.{bm}());")
        test_code.append(f"""    }}""")

    test_code.append("""
}
""")

    with open(os.path.join(output_dir, "test.cpp"), 'w') as f:
        f.write('\n'.join(test_code))


if __name__ == "__main__":
    main()
