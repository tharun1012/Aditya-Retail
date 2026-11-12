import shutil, os
p = "/app/frontend/src/components/CustomerDashboard.js"
s = open(p).read()
if "setRecommendations" in s:
    raise SystemExit("already patched")
a_state = "  const [myProducts, setMyProducts] = useState([]);"
a_map   = "{consumableSuggestions.map((suggestion, idx) => ("
a_tab   = "{/* Service Requests Tab */}"
counts = {"state": s.count(a_state), "map": s.count(a_map), "tab": s.count(a_tab)}
print("anchors:", counts)
if any(v != 1 for v in counts.values()):
    raise SystemExit("ABORT: anchors not unique, nothing written")

state_new = a_state + """
  const [recommendations, setRecommendations] = useState([]);
  useEffect(() => {
    if (!user) return;
    authFetch(`${BACKEND_URL}/api/customer/recommendations?user_id=${user.id}`)
      .then(r => r.json())
      .then(d => setRecommendations(d.status === 'success' ? (d.groups || []) : []))
      .catch(() => setRecommendations([]));
  }, [user, myProducts.length]);"""

section = """{activeTab === 'consumables' && recommendations.length > 0 && (
              <div className="space-y-8 mt-10">
                <h2 className="text-2xl font-bold text-gray-900">Recommended for your products</h2>
                {recommendations.map((g, gi) => (
                  <div key={gi} className="space-y-4">
                    <h3 className="font-semibold text-gray-800">For your {g.for_product}</h3>
                    {[['accessories', 'Accessories and essentials'], ['complete_your_kitchen', 'Complete your kitchen']].map(([key, label]) => (
                      (g[key] || []).length > 0 && (
                        <div key={key}>
                          <p className="text-sm text-gray-500 mb-2">{label}</p>
                          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                            {g[key].map(pr => (
                              <div key={pr.id} className="bg-white rounded-xl shadow-lg p-4 flex flex-col">
                                {pr.image ? <img src={pr.image} alt="" className="h-32 w-full object-contain mb-3" /> : <div className="h-32 mb-3 bg-gray-100 rounded" />}
                                <p className="text-sm font-medium text-gray-900 flex-1">{pr.name}</p>
                                <p className="text-sm font-semibold text-gray-900 mt-2">{pr.price ? formatCurrency(pr.price) : ''}</p>
                                <Link to={`/product/${pr.id}`} className="mt-3 text-center px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">View product</Link>
                              </div>
                            ))}
                          </div>
                        </div>
                      )
                    ))}
                  </div>
                ))}
              </div>
            )}

            """

s = s.replace(a_state, state_new, 1)
s = s.replace(a_map, "{consumableSuggestions.filter(x => x.in_catalog !== false).map((suggestion, idx) => (", 1)
s = s.replace(a_tab, section + a_tab, 1)
os.makedirs("/app/_backup/recofe", exist_ok=True)
shutil.copy(p, "/app/_backup/recofe/CustomerDashboard.js")
open(p, "w").write(s)
print("written OK")
