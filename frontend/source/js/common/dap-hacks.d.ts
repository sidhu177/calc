interface Window {
  /**
   * This is a private function used by the DAP script. It
   * happens to be attached to the global `window` object,
   * which allows us to call it.
   * 
   * Yes, this is horrible.
   */
  _initAutoTracker: Function|undefined
}
