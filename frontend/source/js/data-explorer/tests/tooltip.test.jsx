import toJson from "enzyme-to-json";

import Tooltip from "../components/tooltip";
import makeSetup from "./testSetup";

const defaultProps = {
  children: "",
  text: "hi james",
  show: false
};

const setup = makeSetup(Tooltip, defaultProps);

const tooltipsterMock = jest.fn().mockReturnThis();

// mock the global jquery object function used in <Tooltip>
global.$ = () => {
  const m = jest.fn();
  m.tooltipster = tooltipsterMock;
  return m;
};

describe("<Tooltip>", () => {
  // NOTE: This test does not cover any tooltipster functionality,
  // which has all been mocked
  it("matches snapshot", () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });

  it("initializes tooltipster", () => {
    setup();
    expect(tooltipsterMock.mock.calls.length).toBeGreaterThan(0);
  });
});
