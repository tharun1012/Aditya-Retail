path = "/app/frontend/src/components/CustomerCRM.js"
with open(path, "r") as f:
    content = f.read()

old_fetch = """      setLoading(false);
    } catch (error) {
      console.error('Error fetching customer data:', error);
      setLoading(false);
    }
  };"""

new_fetch = """      setLoading(false);

      // Fetch recent quotations
      try {
        const quotationsRes = await utils.fetchAPI('/api/quotations/list?limit=20');
        const quotationsData = await quotationsRes.json();
        setQuotations(quotationsData.quotations || []);
      } catch (qError) {
        console.error('Error fetching quotations:', qError);
      } finally {
        setQuotationsLoading(false);
      }
    } catch (error) {
      console.error('Error fetching customer data:', error);
      setLoading(false);
      setQuotationsLoading(false);
    }
  };"""

assert old_fetch in content, "fetch block not found"
content = content.replace(old_fetch, new_fetch)

with open(path, "w") as f:
    f.write(content)

print("Fetch block patched successfully.")
