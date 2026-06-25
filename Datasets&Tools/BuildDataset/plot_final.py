import matplotlib.pyplot as plt
import numpy as np

err = ['1e-5','1e-4','1e-3','1e-2','1e-1']
x = np.arange(len(err))

ssim = [0.9765, 0.9780, 0.8739, 0.4406, 0.1679]
valid = [1.0, 1.0, 0.999, 0.9652, 0.8295]
# acuracia max (1e-1 -> 1e-5): 90.3, 98.3, 98.8, 98.1, 99.3  -> reverse to 1e-5->1e-1
acc_raw = [0.903, 0.983, 0.988, 0.981, 0.993]
acc = list(reversed(acc_raw))

fig, ax = plt.subplots(figsize=(9,6))

ax.plot(x, ssim, 'o-', color='#d2691e', label='Mean SSIM')
ax.plot(x, valid, 's--', color='#6699cc', label='Valid Images Used')
ax.plot(x, acc, '^-', color='#2e8b57', label='Max Accuracy')

# Mean SSIM: abaixo da linha (exceto pontos onde ela esta no topo, junto das outras)
ssim_offsets = [(0,-18), (0,-18), (0,-18), (0,-22), (0,-22)]
for (xi, yi), off in zip(zip(x, ssim), ssim_offsets):
    ax.annotate(f'{yi:.4f}', (xi, yi), textcoords="offset points", xytext=off, ha='center', color='#d2691e', fontweight='bold')

# Valid Images Used: acima da linha, levemente para a esquerda
valid_offsets = [(-5,28), (-5,28), (-5,28), (-5,28), (0,-18)]
for (xi, yi), off in zip(zip(x, valid), valid_offsets):
    ax.annotate(f'{yi:g}', (xi, yi), textcoords="offset points", xytext=off, ha='center', color='#6699cc', fontweight='bold')

# Max Accuracy: acima da linha, levemente para a direita
acc_offsets = [(22,12), (22,12), (22,12), (22,12), (0,12)]
for (xi, yi), off in zip(zip(x, acc), acc_offsets):
    ax.annotate(f'{yi:.4f}', (xi, yi), textcoords="offset points", xytext=off, ha='center', color='#2e8b57', fontweight='bold')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.set_xticks(x)
ax.set_xticklabels(err)
ax.set_xlabel('Error Rate')
ax.set_ylabel('Percentage %')
ax.set_ylim(0, 1.22)
ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='lower left')

plt.tight_layout()
plt.savefig('/home/claude/out/ssim_rate_3lines.pdf')
plt.savefig('/home/claude/out/ssim_rate_3lines.png', dpi=150)
print("done")