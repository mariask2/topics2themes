Map.prototype.map = function (f) { return Array.from(this.entries()).map(f) }
Map.prototype.some = function (f) { return Array.from(this.entries()).some(f) }
Map.prototype.setdefault = function (key, defaultValue) {
    if (!this.has(key)) {
        this.set(key, defaultValue)
    }
    return this.get(key)
}

Set.prototype.map = function (f) { return Array.from(this.values()).map(f) }
Set.prototype.some = function (f) { return Array.from(this.values()).some(f) }
Set.prototype.filter = function (f) { return Array.from(this.values()).filter(f) }
Set.prototype.oneValue = function (f) {
    if (this.size > 0) {
	return Array.from(this.values())[0]
    } else {
	return undefined;
    }
}
