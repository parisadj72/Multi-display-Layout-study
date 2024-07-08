using System;
using System.Collections;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class ViewScript : MonoBehaviour, IPointerClickHandler
{
    public Boolean disabledAtStartup = true;
    private Toggle toggle;
    private float wrongClickCounter = 0;
    private string icon;

    public float WrongClickCounter
    {
        get { return wrongClickCounter; }
        set { wrongClickCounter = value; }
    }
    public string Icon
    {
        get { return icon; }
        set { icon = value; }
    }

    private void Awake()
    {
        toggle = GetComponent<Toggle>();
        icon = transform.GetChild(1).GetChild(0).GetComponent<RawImage>().texture.name;

        if (disabledAtStartup)
        {
            DisableInteraction();
        }
    }

    public void UpdateIcon(string name)
    {
        icon = name;
    }

    public bool Status()
    {
        return toggle.isOn;
    }
    public void TurnOn()
    {
        toggle.isOn = true;
    }
    public void TurnOff()
    {
        toggle.isOn = false;
    }

    public void DisableInteraction()
    {
        toggle.interactable = false;
    }
    public void EnableInteraction()
    {
        toggle.interactable = true;
    }
    public void OnPointerClick(PointerEventData eventData)
    {
        if (!toggle.interactable)
            wrongClickCounter++;
    }
}
