using System;
using System.Collections;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using static Experiments;

public class View : MonoBehaviour, ISelectHandler, IDeselectHandler, IPointerClickHandler
{
    private TaskManagement parent;
    private Toggle toggle;
    private string icon;
    private RawImage rawIcon;
    private Color selectedColor;
    private Color normalColor;

    public bool isSelected = false;

    public Boolean disabledAtStartup = true;

    public bool flagViewLookedAt = false;
    public float lookedAtTimer = 0.0f;

    private float wrongClickCounter = 0;
    private float localSelectedTimer = 0.0f;


    public float WrongClickCounter
    {
        get { return wrongClickCounter; }
        set { wrongClickCounter = value; }
    }
    public bool isOn()
    {
        return toggle.isOn;
    }
    public bool isInteractable()
    {
        return toggle.interactable;
    }

    public string Icon
    {
        get { return icon; }
        set { icon = value; }
    }

    public RawImage RawIcon
    {
        get { return rawIcon; }
        set { rawIcon = value; }
    }

    public Color NormalColor { get => normalColor; set => normalColor = value; }
    private void Awake()
    {
        InitializeView();

        if (disabledAtStartup)
        {
            DisableInteraction();
        }
    }

    private void InitializeView()
    {
        parent = GetComponentInParent<TaskManagement>();
        toggle = GetComponent<Toggle>();
        isSelected = false;
        selectedColor = toggle.colors.pressedColor;

        Transform[] children = GetComponentsInChildren<Transform>(true);

        foreach (Transform child in children)
        {
            if (child.gameObject.name == "On")
            {
                //on = child.gameObject;
                rawIcon = child.GetComponentInChildren<RawImage>();
                normalColor = child.GetComponent<Image>().color;
            }
        }
    }

    public void TurnOn()
    {
        toggle.isOn = true;
    }
    public void TurnOff()
    {
        toggle.isOn = false;
    }


    public string GetImage()
    {
        Transform[] children = GetComponentsInChildren<Transform>(true);

        foreach (Transform child in children)
        {
            if (child.gameObject.name == "On")
            {
                rawIcon = child.GetComponentInChildren<RawImage>();
            }
        }
        return rawIcon.texture.name;
    }

    public void SetImage(string image)
    {
        Transform[] children = GetComponentsInChildren<Transform>(true);

        foreach (Transform child in children)
        {
            if (child.gameObject.name == "On")
            {
                rawIcon = child.GetComponentInChildren<RawImage>();
            }
        }
    }

    public void changeColor(Color color)
    {
        Transform[] children = GetComponentsInChildren<Transform>(true);

        foreach (Transform child in children)
        {
            if (child.gameObject.name == "On")
            {
                child.gameObject.GetComponent<Image>().color = color;
            }
        }
    }

    public void DisableInteraction()
    {
        toggle.interactable = false;
    }

    public void EnableInteraction()
    {
        toggle.interactable = true;
    }

    public void OnSelect(BaseEventData eventData)
    {
        /*if (parent.IsExp3())
        {
            if (toggle.isOn && !isSelected)
            {
                isSelected = true;
                StartCoroutine(WaitAndOff());
                parent.SelectedViewsCounter++;
            }
            else
                DisableInteraction();

        }*/
    }
    IEnumerator WaitAndOff()
    {
        yield return new WaitUntil(() => !toggle.isOn);
        TurnOn();
        DisableInteraction();
    }
    public void OnDeselect(BaseEventData eventData)
    {
        /*if (parent.IsExp3())
        {
            TurnOn();
            EnableInteraction();
            if (parent.SelectedViewsCounter == 1)
                changeColor(selectedColor);
        }*/
    }


    public void OnPointerClick(PointerEventData eventData)
    {
        if (parent.IsExp3())
        {
            if (toggle.interactable && !isSelected)
            {
                isSelected = true;
                parent.SelectedViewsCounter++;
                TurnOn();
                EnableInteraction();
                changeColor(selectedColor);
            }
            else if (isSelected)
            {
                TurnOn();
            }
        }

        // Counting Errors...
        if (!toggle.interactable)
        {
            wrongClickCounter++;
        }
        if (toggle.interactable && !parent.IsExp3())
        {
            System.IO.File.AppendAllText(GameObject.FindGameObjectWithTag("experiment").GetComponent<Experiments>().timerFilePath, "Time per selection = " + localSelectedTimer + "\n \n");
            localSelectedTimer = 0;
        }
    }
    private void Update()
    {
        if (GameObject.FindGameObjectWithTag("experiment").GetComponent<Experiments>().experiment == Experiment.Exp1 && toggle.isOn)
        {
            lookedAtTimer += Time.deltaTime;
            localSelectedTimer += Time.deltaTime;
        }
        if(GameObject.FindGameObjectWithTag("experiment").GetComponent<Experiments>().experiment == Experiment.Exp2 && !toggle.isOn && toggle.interactable)
        {
            lookedAtTimer += Time.deltaTime;
            localSelectedTimer += Time.deltaTime;
        }
    }
}
