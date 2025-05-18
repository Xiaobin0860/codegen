import random
from typing import List
import sys

registers = ['x9', 'x10', 'x11', 'x12', 'x13', 'x14', 'x15']
operations = ['add', 'sub', 'eor', 'orr', 'and', 'mov', 'bic', 'orn', 'lsl', 'lsr', 'asr']
nop_variants = [
    "nop",
    "mov xzr, xzr",
    "add xzr, xzr, #0",
    "sub xzr, xzr, #0",
    "and xzr, xzr, xzr",
    "orr xzr, xzr, xzr"
]


def generate_junk_insn(avoid_regs: list = None) -> str:
    """生成单条垃圾指令序列"""
    # 排除最近使用的寄存器（可选）
    available_regs = registers.copy()
    if avoid_regs:
        available_regs = [r for r in available_regs if r not in avoid_regs]

    num_regs = random.choice([1, 2])
    selected = random.sample(available_regs, num_regs)
    selected.sort()

    code = []
    stack_offset = random.choice([-16, -32, -48])
    # 保存指令
    if len(selected) == 1:
        code.append(f"str {selected[0]}, [sp, #{stack_offset}]!")
    else:
        code.append(f"stp {selected[0]}, {selected[1]}, [sp, #{stack_offset}]!")

    # 垃圾指令核心
    for _ in range(random.randint(3, 5)):
        reg = random.choice(selected)
        op = random.choice(operations)

        if op in ['add', 'sub']:
            imm = random.randint(1, 4095)
            code.append(f"{op} {reg}, {reg}, #{imm}")
            code.append(f"{'sub' if op == 'add' else 'add'} {reg}, {reg}, #{imm}")
        elif op in ['eor', 'bic', 'orn']:
            operand = reg if op == 'eor' else random.choice(['xzr', reg])
            code.append(f"{op} {reg}, {reg}, {operand}")
        elif op in ['lsl', 'lsr', 'asr']:
            shift = random.randint(1, 63)
            code.append(f"{op} {reg}, {reg}, #{shift}")
            code.append(f"{'lsr' if op == 'lsl' else 'lsl'} {reg}, {reg}, #{shift}")
        elif op == 'orr':
            code.append(f"orr {reg}, {reg}, xzr")
        elif op == 'and':
            code.append(f"and {reg}, {reg}, {reg}")
        elif op == 'mov':
            parts = random.sample([0, 16, 32, 48], 2)
            for shift in sorted(parts, reverse=True):
                imm = random.randint(0, 0xFFFF)
                code.append(f"movk {reg}, #0x{imm:04x}, lsl #{shift}")
        if random.random() < 0.3:
            code.extend([
                f"cmp {reg}, {reg}",
                "b.eq .+4",
                "b .+8",
                "nop",
                "nop"
            ])

    # 恢复指令
    if len(selected) == 1:
        code.append(f"ldr {selected[0]}, [sp], #{-stack_offset}")
    else:
        code.append(f"ldp {selected[0]}, {selected[1]}, [sp], #{-stack_offset}")

    # 添加随机nop
    code.append(random.choice(nop_variants))

    return code, selected


def generate_obfuscation_code(num_blocks: int) -> List[str]:
    """生成指定数量的混淆代码块"""
    generated = []
    last_regs = []

    for _ in range(num_blocks):
        code_block, used_regs = generate_junk_insn(avoid_regs=last_regs[-2:] if last_regs else None)
        last_regs = used_regs
        asm_code = ';'.join(code_block)
        generated.append(f'__asm__ __volatile__("{asm_code}" ::: "memory")')

    return generated


if __name__ == "__main__":
    num_blocks = 500
    if len(sys.argv) > 1:
        try:
            num_blocks = int(sys.argv[1])
            if num_blocks <= 0:
                raise ValueError
        except ValueError:
            print("Error: Please provide a positive integer argument")
            sys.exit(1)

    generated = generate_obfuscation_code(num_blocks)

    with open('arm64_blocks.h', 'w', encoding='utf-8') as h_file:
        h_file.write("#ifndef FLOWER_BLOCKS_H\n")
        h_file.write("#define FLOWER_BLOCKS_H\n\n")
        for idx, code in enumerate(generated, 1):
            h_file.write(f"#define FLOWER_BLOCK_{idx:03d}() {code}\n\n")
        h_file.write('\n#endif // FLOWER_BLOCKS_H\n')
