using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit;

public class Socket : MonoBehaviour
{
    public RawImage LastIcon;
    /*public string LastIcon
    {
        get { return lastIcon; }
        set { lastIcon = value; }
    }
    void Start()
    {
        IXRSelectInteractable obj = GetComponent<XRSocketInteractor>().firstInteractableSelected;
        if (obj.transform.GetComponent<ViewScript>() != null)
        {
            lastIcon = obj.transform.GetComponent<ViewScript>().Icon;
        }
    }*/
    public void OnAttach()
    {
        List<IXRSelectInteractable> obj = GetComponent<XRSocketInteractor>().interactablesSelected;
        if (obj[0].transform.GetComponent<ViewScript>() != null)
        {
            LastIcon = obj[0].transform.GetChild(1).GetChild(0).GetComponent<RawImage>();
        }
    }
}
