import shutil, os
p = "/app/frontend/src/components/CustomerDashboard.js"
s = open(p).read()
if "addedCartId" in s:
    raise SystemExit("already patched")
imp = "import HomeTab from './HomeTab';"
st  = "  const [recommendations, setRecommendations] = useState([]);"
lnk = '<Link to={`/product/${pr.id}`} className="mt-3 text-center px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">View product</Link>'
counts = {"import": s.count(imp), "state": s.count(st), "link": s.count(lnk)}
print("anchors:", counts)
if any(v != 1 for v in counts.values()):
    raise SystemExit("ABORT: anchors not unique, nothing written")

s = s.replace(imp, imp + "\nimport { useCart } from './CartContext';", 1)
s = s.replace(st, st + """
  let cartApi = null;
  try { cartApi = useCart(); } catch (e) { cartApi = null; }
  const [addedCartId, setAddedCartId] = useState(null);
  const addRecoToCart = (pr) => {
    if (!cartApi || !cartApi.addToCart) { navigate(`/product/${pr.id}`); return; }
    cartApi.addToCart({ ...pr, images: pr.image ? [pr.image] : [] }, 1);
    setAddedCartId(pr.id);
    setTimeout(() => setAddedCartId(null), 2000);
  };""", 1)
new_btns = """<div className="mt-3 flex flex-col gap-2">
                                  <button onClick={() => addRecoToCart(pr)} className="px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
                                    {addedCartId === pr.id ? 'Added to cart \u2713' : 'Add to cart'}
                                  </button>
                                  <Link to={`/product/${pr.id}`} className="text-center px-3 py-2 bg-gray-100 text-gray-800 rounded-lg text-sm hover:bg-gray-200">View product</Link>
                                </div>"""
s = s.replace(lnk, new_btns, 1)
os.makedirs("/app/_backup/addcart", exist_ok=True)
shutil.copy(p, "/app/_backup/addcart/CustomerDashboard.js")
open(p, "w").write(s)
print("written OK")
