import shutil, os
p = "/app/frontend/src/components/CustomerDashboard.js"
s = open(p).read()
if "const ok = await cartApi.addToCart" in s:
    raise SystemExit("already patched")
imp = "import { useCart } from './CartContext';"
fn  = "const addRecoToCart = (pr) => {"
old = """    if (!cartApi || !cartApi.addToCart) { navigate(`/product/${pr.id}`); return; }
    cartApi.addToCart({ ...pr, images: pr.image ? [pr.image] : [] }, 1);
    setAddedCartId(pr.id);
    setTimeout(() => setAddedCartId(null), 2000);"""
counts = {"import": s.count(imp), "fn": s.count(fn), "body": s.count(old)}
print("anchors:", counts)
if any(v != 1 for v in counts.values()):
    raise SystemExit("ABORT: anchors not unique, nothing written")
new = """    if (!cartApi || !cartApi.addToCart) { alert('Cart is not available right now. Please use View product.'); return; }
    const ok = await cartApi.addToCart(pr.id, 1);
    if (ok) {
      setAddedCartId(pr.id);
      setTimeout(() => setAddedCartId(null), 2000);
    } else {
      alert('Could not add this item to the cart. Please try again.');
    }"""
s = s.replace(imp, "import { useCart } from '../hooks/useCart';", 1)
s = s.replace(fn, "const addRecoToCart = async (pr) => {", 1)
s = s.replace(old, new, 1)
os.makedirs("/app/_backup/cartfix", exist_ok=True)
shutil.copy(p, "/app/_backup/cartfix/CustomerDashboard.js")
open(p, "w").write(s)
print("written OK")
