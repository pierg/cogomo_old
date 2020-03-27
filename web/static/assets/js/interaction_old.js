document.addEventListener("DOMContentLoaded", function () {
    var cy = (window.cy = cytoscape({
        container: document.getElementById("cy"),
        style: [
            {
                selector: "node[type='goal']",
                css: {
                    content: "data(id)",
                    "font-family": "monospace",
                    "font-size": "0.7em",
                    "text-valign": "center",
                    "text-halign": "center",
                    height: "30px",
                    width: "100px",
                    shape: "rectangle",
                    "background-color": "DodgerBlue"
                }
            },
            {
                selector: "node[type='composition']",
                css: {
                    content: "||",
                    "font-family": "monospace",
                    "font-size": "0.7em",
                    "text-valign": "center",
                    "text-halign": "center",
                    height: "30px",
                    width: "30px",
                    shape: "circle",
                    "background-color": "MediumSeaGreen"
                }
            },
            {
                selector: "node[type='conjunction']",
                css: {
                    content: "/\\",
                    "font-family": "monospace",
                    "font-size": "0.7em",
                    "text-valign": "center",
                    "text-halign": "center",
                    height: "30px",
                    width: "30px",
                    shape: "circle",
                    "background-color": "MediumSeaGreen"
                }
            },
            {
                selector: "node[type='refinement']",
                css: {
                    content: "R",
                    "font-family": "monospace",
                    "font-size": "0.7em",
                    "text-valign": "center",
                    "text-halign": "center",
                    height: "30px",
                    width: "30px",
                    shape: "circle",
                    "background-color": "MediumSeaGreen"
                }
            },
            {
                selector: "node[type='mapping']",
                css: {
                    content: "M",
                    "font-family": "monospace",
                    "font-size": "0.7em",
                    "text-valign": "center",
                    "text-halign": "center",
                    height: "30px",
                    width: "30px",
                    shape: "circle",
                    "background-color": "MediumSeaGreen"
                }
            },
            {
                selector: "edge[type='input']",
                css: {
                    "curve-style": "bezier",
                    "control-point-step-size": 1,
                    "source-arrow-shape": "triangle",
                    'width': 1,
                }
            },
            {
                selector: "edge[type='refinement']",
                css: {
                    "curve-style": "bezier",
                    "control-point-step-size": 40,
                    "source-arrow-shape": "triangle-backcurve",

                }
            }
        ],

        elements: {
            nodes: [
                {
                    data: {
                        type: "goal",
                        id: "node1",
                        description: "description",
                        assumptions: "ASSUMPTIONS_GOAL_1",
                        guarantees: "GUARANTEES_GOAL_1"
                    }
                },
                {data: {id: "1-234", type: "conjunction"}},
                {data: {id: "2", type: "goal"}},
                {data: {id: "3", type: "goal"}},
                {data: {id: "4", type: "goal"}}
            ],
            edges: [
                {data: {source: "node1", target: "1-234", type: "refinement"}},
                {data: {source: "1-234", target: "2", type: "input"}},
                {data: {source: "1-234", target: "3", type: "input"}},
                {data: {source: "1-234", target: "4", type: "input"}}
            ]
        },
        layout: {
            name: "dagre"
        }
    }));

    function makePopper(ele) {
        let ref = ele.popperRef(); // used only for positioning

        ele.tippy = tippy(ref, { // tippy options:
            content: () => {
                let content = document.createElement('div');

                content.innerHTML = ele.data("assumptions");

                return content;
            },
            trigger: 'manual' // probably want manual mode
        });
    }

    cy.ready(function () {
        cy.nodes().forEach(function (ele) {
            makePopper(ele);
        });
    });

    cy.nodes().unbind('mouseover');
    cy.nodes().bind('mouseover', (event) => event.target.tippy.show());

    cy.nodes().unbind('mouseout');
    cy.nodes().bind('mouseout', (event) => event.target.tippy.hide());
    cy.bind('click', 'node', function (evt) {
        var inst = $('[data-remodal-id=modal2]').remodal();
        if (typeof inst !== "undefined") {
            inst.open();
        }
        //
        // cy.elements().layout(
        //     {
        //         name: 'dagre',
        //     }).run();
    });


});