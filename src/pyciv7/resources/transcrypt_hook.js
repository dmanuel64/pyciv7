(async () => {
    try {
        const mod = await import('fs://game/<REL_PATH>');

        // Transcrypt usually exports { test } or default, or direct names
        // const ns = mod.test || mod.default || mod;
        // optional: expose for non-module code
        // window.mod_name = ns;
    } catch (e) {
        console.error('Failed to import test.js', e);
    }
})();