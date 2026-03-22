import re

with open('/Users/k.far.88/.gemini/antigravity/scratch/perdiem-pseo/reciprocity_index_builder.py', 'r') as f:
    text = f.read()

script_block = """<script>
const input = document.getElementById('stateSearch');
const searchClear = document.getElementById('searchClear');
const allRows = [...document.querySelectorAll('.row')];
const groups = [...document.querySelectorAll('.group')];
const sortSelect = document.getElementById('sortSelect');
const emptyState = document.getElementById('emptyState');
const pathBtns = [...document.querySelectorAll('[data-filter-group="path"] .seg-btn')];

let pathFilter = 'all';

function tierRank(v) {{
  if (v === 'none') return 0;
  if (v === 'fast') return 1;
  if (v === 'mid') return 2;
  return 3;
}}

function sortRows(rows) {{
  const mode = sortSelect.value;
  return [...rows].sort((a, b) => {{
    if (mode === 'fee') return Number(a.dataset.fee) - Number(b.dataset.fee);
    if (mode === 'difficulty') {{
      const d = tierRank(a.dataset.tier) - tierRank(b.dataset.tier);
      if (d !== 0) return d;
      return Number(a.dataset.fee) - Number(b.dataset.fee);
    }}
    return a.dataset.state.localeCompare(b.dataset.state);
  }});
}}

function syncUrl() {{
  const params = new URLSearchParams(window.location.search);
  const q = input.value.trim();
  if (q) params.set('q', q); else params.delete('q');
  if (pathFilter !== 'all') params.set('path', pathFilter); else params.delete('path');
  if (sortSelect.value !== 'state') params.set('sort', sortSelect.value); else params.delete('sort');
  const next = params.toString();
  const target = next ? `${{window.location.pathname}}?${{next}}` : window.location.pathname;
  window.history.replaceState(null, '', target);
}}

function applyFilters() {{
  const q = input.value.toLowerCase().trim();
  searchClear.style.display = q ? 'flex' : 'none';
  let shown = 0;

  for (const row of allRows) {{
    const matchQ = row.dataset.state.includes(q);
    const matchP = pathFilter === 'all' || row.dataset.path === pathFilter;
    const visible = matchQ && matchP;
    row.style.display = visible ? '' : 'none';
    if (visible) shown++;
  }}

  document.querySelectorAll('.group-rows').forEach(container => {{
    const fragment = document.createDocumentFragment();
    const visible = [...container.querySelectorAll('.row')].filter(r => r.style.display !== 'none');
    const hidden = [...container.querySelectorAll('.row')].filter(r => r.style.display === 'none');
    
    const sortedVisible = sortRows(visible);
    
    for (const r of sortedVisible) {{
      r.classList.remove('no-border');
      fragment.appendChild(r);
    }}
    if (sortedVisible.length > 0) {{
      sortedVisible[sortedVisible.length - 1].classList.add('no-border');
    }}
    
    for (const r of hidden) {{
      r.classList.remove('no-border');
      fragment.appendChild(r);
    }}
    
    container.appendChild(fragment);
  }});

  for (const g of groups) {{
    const container = g.querySelector('.group-rows');
    if (!container) continue;
    const hasVisible = [...container.querySelectorAll('.row')].some(r => r.style.display !== 'none');
    g.style.display = hasVisible ? '' : 'none';
  }}

  emptyState.style.display = shown === 0 ? 'block' : 'none';
  syncUrl();
}}

input.addEventListener('input', () => requestAnimationFrame(applyFilters));
searchClear.addEventListener('click', () => {{
  input.value = '';
  input.focus();
  requestAnimationFrame(applyFilters);
}});
sortSelect.addEventListener('change', () => requestAnimationFrame(applyFilters));

for (const btn of pathBtns) {{
  btn.addEventListener('click', () => {{
    pathFilter = btn.dataset.value;
    for (const b of pathBtns) {{
      const isActive = b.dataset.value === pathFilter;
      b.classList.toggle('active', isActive);
      b.setAttribute('aria-pressed', isActive.toString());
    }}
    requestAnimationFrame(applyFilters);
  }});
}}

const params = new URLSearchParams(window.location.search);
if (params.get('q')) input.value = params.get('q');
if (params.get('path') && ['all','member','non-member','cdr-only'].includes(params.get('path'))) pathFilter = params.get('path');
if (params.get('sort') && ['state','fee','difficulty'].includes(params.get('sort'))) sortSelect.value = params.get('sort');

for (const b of pathBtns) {{
  const isActive = b.dataset.value === pathFilter;
  b.classList.toggle('active', isActive);
  b.setAttribute('aria-pressed', isActive.toString());
}}

requestAnimationFrame(applyFilters);
</script>"""

new_text = re.sub(r'<script>.*?</script>', script_block, text, flags=re.DOTALL)

with open('/Users/k.far.88/.gemini/antigravity/scratch/perdiem-pseo/reciprocity_index_builder.py', 'w') as f:
    f.write(new_text)

print("JS block substituted successfully.")
